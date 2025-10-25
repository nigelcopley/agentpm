/**
 * Product type definitions matching backend Django models
 */

export interface Category {
  id: number
  name: string
  slug: string
  description: string
  image?: string
  parent?: number
  children?: Category[]
  product_count: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProductImage {
  id: number
  image: string
  alt_text: string
  position: number
}

export interface ProductReview {
  id: number
  user: number
  user_name: string
  rating: number
  title: string
  comment: string
  is_verified_purchase: boolean
  created_at: string
}

export interface Product {
  id: number
  name: string
  slug: string
  sku: string
  category: Category
  description: string
  price: string
  compare_at_price?: string
  is_on_sale: boolean
  discount_percentage: number
  stock_quantity: number
  weight: string
  is_active: boolean
  is_featured: boolean
  images: ProductImage[]
  reviews: ProductReview[]
  average_rating?: number
  review_count: number
  created_at: string
  updated_at: string
}

export interface ProductListItem {
  id: number
  name: string
  slug: string
  sku: string
  category_name: string
  price: string
  compare_at_price?: string
  is_on_sale: boolean
  discount_percentage: number
  primary_image?: ProductImage
  average_rating?: number
  is_featured: boolean
}

export interface ProductFilters {
  category?: string
  min_price?: number
  max_price?: number
  on_sale?: boolean
  in_stock?: boolean
  search?: string
  ordering?: string
}
