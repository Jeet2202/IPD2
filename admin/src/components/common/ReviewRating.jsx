import React from 'react';
import { Star } from 'lucide-react';

export default function ReviewRating({ rating, size = 'sm', showValue = true }) {
  const numericRating = Number(rating) || 0;
  const isLowRating = numericRating <= 2.0;

  const iconSizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const currentSize = iconSizes[size] || iconSizes.sm;

  return (
    <div className="flex items-center gap-1.5 shrink-0">
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`${currentSize} ${
              star <= Math.round(numericRating)
                ? isLowRating
                  ? 'fill-[#EF4444] text-[#EF4444]'
                  : 'fill-[#F59E0B] text-[#F59E0B]'
                : 'fill-[#E2E8F0] text-[#CBD5E1]'
            }`}
          />
        ))}
      </div>
      {showValue && (
        <span
          className={`text-xs font-bold ${
            isLowRating ? 'text-[#DC2626]' : 'text-[#0F172A]'
          }`}
        >
          {numericRating.toFixed(1)}
        </span>
      )}
    </div>
  );
}
