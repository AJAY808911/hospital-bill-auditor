"""
Optional AI Integration Service.
Decoupled, safe, and strictly optional.
Core calculations NEVER rely on AI.
"""
import os
import json
from typing import Dict, Any, List, Optional
import httpx
from app.engine.categories import BillCategory, normalize_category_from_description

class AIService:
    @staticmethod
    def get_provider_status() -> Dict[str, Any]:
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if gemini_key:
            return {
                "enabled": True,
                "provider": "Google Gemini",
                "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                "status": "Configured via GEMINI_API_KEY environment variable.",
            }
        elif openai_key:
            return {
                "enabled": True,
                "provider": "OpenAI",
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "status": "Configured via OPENAI_API_KEY environment variable.",
            }
        else:
            return {
                "enabled": False,
                "provider": "None (Deterministic Rule Heuristics Active)",
                "model": "Local Rule Categorizer",
                "status": "No external AI API key configured. Deterministic regex & keyword heuristics are handling categorization and explanations.",
                "setup_guide": (
                    "To enable AI features, set GEMINI_API_KEY or OPENAI_API_KEY in your environment or .env file. "
                    "Core calculations remain 100% functional without AI."
                )
            }

    @classmethod
    async def suggest_categories(cls, descriptions: List[str]) -> List[Dict[str, Any]]:
        """
        Suggests categories for a list of descriptions.
        If AI is enabled and reachable, asks LLM; otherwise falls back to deterministic heuristics.
        """
        provider = cls.get_provider_status()
        
        # Fallback heuristic always works
        heuristic_results = [
            {
                "description": desc,
                "suggested_category": normalize_category_from_description(desc).value,
                "source": "Deterministic Heuristic",
                "confidence": 0.9 if normalize_category_from_description(desc) != BillCategory.AMBIGUOUS_UNCATEGORIZED else 0.4
            }
            for desc in descriptions
        ]

        if not provider["enabled"]:
            return heuristic_results

        # If key is available, attempt call with timeout
        # If any error occurs (network, rate limit, quota), seamlessly fallback to heuristic
        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}:generateContent?key={gemini_key}"
                prompt = (
                    "Classify each of the following hospital bill line item descriptions into one of these exact categories: "
                    f"{[c.value for c in BillCategory]}.\n"
                    f"Return a strict JSON array of objects with keys: 'description', 'suggested_category', 'reasoning'.\n"
                    f"Items: {json.dumps(descriptions)}"
                )
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(
                        url,
                        json={"contents": [{"parts": [{"text": prompt}]}]}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                        # Extract JSON from response
                        start = text_content.find("[")
                        end = text_content.rfind("]")
                        if start != -1 and end != -1:
                            parsed = json.loads(text_content[start:end+1])
                            return [
                                {
                                    "description": item.get("description"),
                                    "suggested_category": item.get("suggested_category", BillCategory.AMBIGUOUS_UNCATEGORIZED.value),
                                    "source": "Gemini AI",
                                    "confidence": 0.95
                                }
                                for item in parsed
                            ]
        except Exception:
            # Fall back safely
            pass

        return heuristic_results

    @classmethod
    async def generate_plain_language_summary(cls, audit_summary_dict: Dict[str, Any]) -> str:
        """
        Generates a human-friendly narrative explaining the audit results.
        If AI is unavailable, constructs a clear, deterministic explanation template.
        """
        billed = audit_summary_dict.get("total_billed", 0)
        payable = audit_summary_dict.get("total_estimated_payable", 0)
        shortfall = audit_summary_dict.get("total_estimated_shortfall", 0)
        item_ded = audit_summary_dict.get("item_level_deductions", 0)
        copay = audit_summary_dict.get("copay_applied", 0)
        deductible = audit_summary_dict.get("deductible_applied", 0)

        # Standard deterministic explanation template
        lines = [
            f"Based on your health insurance policy audit, out of the total billed amount of Rs. {billed:,.2f}, "
            f"an estimated Rs. {payable:,.2f} is payable, resulting in a potential shortfall of Rs. {shortfall:,.2f}."
        ]

        if item_ded > 0:
            lines.append(
                f"• Item-level deductions total Rs. {item_ded:,.2f}, which typically include non-payable consumables "
                f"(e.g., gloves, masks, administrative charges) or room-rent limit excesses and associated proportionate deductions."
            )
        if copay > 0:
            lines.append(f"• Co-payment deduction of Rs. {copay:,.2f} applies as the insured patient's co-share percentage.")
        if deductible > 0:
            lines.append(f"• Mandatory policy deductible of Rs. {deductible:,.2f} has been deducted from admissible expenses.")

        lines.append(
            "Please note: These figures are pre-claim estimates based on standard insurance guidelines and your configured policy. "
            "Actual settlement may differ based on your insurer's final medical underwriting review."
        )

        return "\n\n".join(lines)

