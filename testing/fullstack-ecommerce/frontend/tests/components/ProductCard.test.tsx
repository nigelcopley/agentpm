/**
 * Tests for ProductCard component
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect } from '@jest/globals'
import ProductCard from '@/components/products/ProductCard'
import type { ProductListItem } from '@/types/product'

// Mock TanStack Router
jest.mock('@tanstack/react-router', () => ({
  Link: ({ children, to }: any) => <a href={to}>{children}</a>,
}))

describe('ProductCard', () => {
  const mockProduct: ProductListItem = {
    id: 1,
    name: 'Test Product',
    slug: 'test-product',
    sku: 'TEST-001',
    category_name: 'Electronics',
    price: '99.99',
    compare_at_price: undefined,
    is_on_sale: false,
    discount_percentage: 0,
    primary_image: {
      id: 1,
      image: 'https://example.com/image.jpg',
      alt_text: 'Test product image',
      position: 0,
    },
    average_rating: 4.5,
    is_featured: false,
  }

  it('renders product information', () => {
    render(<ProductCard product={mockProduct} />)

    expect(screen.getByText('Test Product')).toBeInTheDocument()
    expect(screen.getByText('$99.99')).toBeInTheDocument()
    expect(screen.getByText('4.5')).toBeInTheDocument()
  })

  it('displays sale badge when product is on sale', () => {
    const saleProduct = {
      ...mockProduct,
      is_on_sale: true,
      compare_at_price: '149.99',
      discount_percentage: 33,
    }

    render(<ProductCard product={saleProduct} />)

    expect(screen.getByText('SALE')).toBeInTheDocument()
    expect(screen.getByText('-33%')).toBeInTheDocument()
    expect(screen.getByText('$149.99')).toBeInTheDocument()
  })

  it('handles product without image', () => {
    const noImageProduct = {
      ...mockProduct,
      primary_image: undefined,
    }

    render(<ProductCard product={noImageProduct} />)

    expect(screen.getByText('No image')).toBeInTheDocument()
  })

  it('links to product detail page', () => {
    render(<ProductCard product={mockProduct} />)

    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/products/test-product')
  })
})
