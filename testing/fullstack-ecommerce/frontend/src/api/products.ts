/**
 * Product API service using TanStack Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import type { Product, ProductListItem, ProductFilters, ProductReview } from '@/types/product'

// Query keys for caching
export const productKeys = {
  all: ['products'] as const,
  lists: () => [...productKeys.all, 'list'] as const,
  list: (filters: ProductFilters) => [...productKeys.lists(), { filters }] as const,
  details: () => [...productKeys.all, 'detail'] as const,
  detail: (slug: string) => [...productKeys.details(), slug] as const,
  reviews: (slug: string) => [...productKeys.all, 'reviews', slug] as const,
}

// API functions
const productApi = {
  getProducts: async (filters: ProductFilters = {}): Promise<ProductListItem[]> => {
    const { data } = await apiClient.get('/products/', { params: filters })
    return data.results || data
  },

  getProduct: async (slug: string): Promise<Product> => {
    const { data } = await apiClient.get(`/products/${slug}/`)
    return data
  },

  getFeaturedProducts: async (): Promise<ProductListItem[]> => {
    const { data } = await apiClient.get('/products/featured/')
    return data
  },

  searchProducts: async (query: string): Promise<ProductListItem[]> => {
    const { data } = await apiClient.get('/products/search/', {
      params: { q: query }
    })
    return data.results
  },

  getProductReviews: async (slug: string): Promise<ProductReview[]> => {
    const { data } = await apiClient.get(`/products/${slug}/reviews/`)
    return data
  },

  addReview: async ({ slug, review }: { slug: string; review: Partial<ProductReview> }) => {
    const { data } = await apiClient.post(`/products/${slug}/add_review/`, review)
    return data
  },
}

// React Query hooks
export const useProducts = (filters: ProductFilters = {}) => {
  return useQuery({
    queryKey: productKeys.list(filters),
    queryFn: () => productApi.getProducts(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useProduct = (slug: string) => {
  return useQuery({
    queryKey: productKeys.detail(slug),
    queryFn: () => productApi.getProduct(slug),
    enabled: !!slug,
  })
}

export const useFeaturedProducts = () => {
  return useQuery({
    queryKey: [...productKeys.lists(), 'featured'],
    queryFn: productApi.getFeaturedProducts,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const useProductSearch = (query: string) => {
  return useQuery({
    queryKey: [...productKeys.lists(), 'search', query],
    queryFn: () => productApi.searchProducts(query),
    enabled: query.length > 2,
  })
}

export const useProductReviews = (slug: string) => {
  return useQuery({
    queryKey: productKeys.reviews(slug),
    queryFn: () => productApi.getProductReviews(slug),
    enabled: !!slug,
  })
}

export const useAddReview = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: productApi.addReview,
    onSuccess: (data, variables) => {
      // Invalidate product details and reviews
      queryClient.invalidateQueries({
        queryKey: productKeys.detail(variables.slug)
      })
      queryClient.invalidateQueries({
        queryKey: productKeys.reviews(variables.slug)
      })
    },
  })
}
