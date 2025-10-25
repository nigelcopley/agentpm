/**
 * Product listing page with filters
 */

import { useState } from 'react'
import { useProducts } from '@/api/products'
import ProductCard from '@/components/products/ProductCard'
import type { ProductFilters } from '@/types/product'

export default function ProductListPage() {
  const [filters, setFilters] = useState<ProductFilters>({})
  const { data: products, isLoading, error } = useProducts(filters)

  const handleFilterChange = (key: keyof ProductFilters, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          Error loading products. Please try again.
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex gap-8">
        {/* Filters Sidebar */}
        <aside className="w-64 flex-shrink-0">
          <div className="sticky top-4 space-y-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Price Range</h3>
              <div className="space-y-2">
                <input
                  type="number"
                  placeholder="Min price"
                  className="w-full px-3 py-2 border rounded-md"
                  onChange={(e) => handleFilterChange('min_price', e.target.value)}
                />
                <input
                  type="number"
                  placeholder="Max price"
                  className="w-full px-3 py-2 border rounded-md"
                  onChange={(e) => handleFilterChange('max_price', e.target.value)}
                />
              </div>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-3">Filters</h3>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300"
                    onChange={(e) => handleFilterChange('on_sale', e.target.checked)}
                  />
                  <span className="ml-2 text-sm">On Sale</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300"
                    onChange={(e) => handleFilterChange('in_stock', e.target.checked)}
                  />
                  <span className="ml-2 text-sm">In Stock</span>
                </label>
              </div>
            </div>

            <button
              onClick={() => setFilters({})}
              className="w-full px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
            >
              Clear Filters
            </button>
          </div>
        </aside>

        {/* Product Grid */}
        <main className="flex-1">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Products</h1>
            <span className="text-sm text-gray-600">
              {products?.length || 0} products
            </span>
          </div>

          {products && products.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              No products found
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
