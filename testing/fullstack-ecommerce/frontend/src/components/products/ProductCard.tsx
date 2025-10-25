/**
 * Product card component for product listings
 */

import { Link } from '@tanstack/react-router'
import type { ProductListItem } from '@/types/product'

interface ProductCardProps {
  product: ProductListItem
}

export default function ProductCard({ product }: ProductCardProps) {
  const {
    slug,
    name,
    price,
    compare_at_price,
    is_on_sale,
    discount_percentage,
    primary_image,
    average_rating,
  } = product

  return (
    <div className="group relative border rounded-lg p-4 hover:shadow-lg transition-shadow">
      <Link to={`/products/${slug}`} className="block">
        {/* Product Image */}
        <div className="aspect-square bg-gray-100 rounded-md overflow-hidden mb-4">
          {primary_image ? (
            <img
              src={primary_image.image}
              alt={primary_image.alt_text || name}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform"
            />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              No image
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-2">
          <h3 className="font-medium text-gray-900 line-clamp-2 group-hover:text-blue-600">
            {name}
          </h3>

          {/* Rating */}
          {average_rating && (
            <div className="flex items-center text-sm">
              <span className="text-yellow-500">★</span>
              <span className="ml-1 text-gray-600">{average_rating.toFixed(1)}</span>
            </div>
          )}

          {/* Price */}
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold text-gray-900">
              ${parseFloat(price).toFixed(2)}
            </span>

            {is_on_sale && compare_at_price && (
              <>
                <span className="text-sm text-gray-500 line-through">
                  ${parseFloat(compare_at_price).toFixed(2)}
                </span>
                <span className="text-sm font-medium text-red-600">
                  -{discount_percentage}%
                </span>
              </>
            )}
          </div>
        </div>

        {/* Sale Badge */}
        {is_on_sale && (
          <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded text-xs font-medium">
            SALE
          </div>
        )}
      </Link>
    </div>
  )
}
