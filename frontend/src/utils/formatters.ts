export function formatINR(val: number | undefined | null): string {
  if (val === undefined || val === null || isNaN(val)) return '₹0.00';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }).format(val);
}

export function formatPercent(val: number | undefined | null): string {
  if (val === undefined || val === null || isNaN(val)) return '0.0%';
  return `${val.toFixed(1)}%`;
}

export function formatDate(dateString: string | undefined | null): string {
  if (!dateString) return 'N/A';
  try {
    const d = new Date(dateString);
    return d.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateString;
  }
}

