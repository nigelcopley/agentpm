# ADR-002: TanStack Query Over Redux for State Management

## Status
Accepted

## Context
Frontend applications need state management for server data, UI state, and caching. Traditional approaches use Redux, MobX, or context API. Modern solutions like TanStack Query (React Query) specialize in server state management.

## Decision
We will use **TanStack Query for server state** and **Zustand for client-side UI state**.

## Rationale

### TanStack Query Advantages:
1. **Server State Specialization**: Built specifically for async server data
2. **Automatic Caching**: Smart caching with configurable staleness
3. **Background Refetching**: Keeps data fresh automatically
4. **Optimistic Updates**: Built-in support for optimistic UI
5. **DevTools Integration**: Excellent debugging experience
6. **TypeScript Support**: Full type safety with minimal configuration

### Why Not Redux:
1. Redux requires significant boilerplate for async operations
2. Redux Toolkit Query is similar to TanStack Query but less mature
3. Redux mixes server and client state management
4. More complex mental model for simple data fetching

### Zustand for UI State:
- Minimal API, zero boilerplate
- Perfect for client-side UI state (modals, theme, sidebar)
- Works seamlessly with TanStack Query

## Implementation

```typescript
// TanStack Query for server state
const { data, isLoading } = useProducts({ category: 'electronics' })

// Zustand for UI state
const { isCartOpen, toggleCart } = useCartStore()
```

## Consequences

### Positive:
- Reduced boilerplate (no actions, reducers for server data)
- Better performance (automatic request deduplication)
- Improved UX (background refetching, optimistic updates)
- Easier testing (separation of concerns)

### Negative:
- Team needs to learn new patterns (different from Redux)
- Two state management solutions instead of one
- Less standardization (Redux is more widely known)

## Metrics
- **Bundle Size**: TanStack Query (12KB) + Zustand (1KB) vs Redux Toolkit (45KB)
- **Boilerplate Reduction**: ~60% less code for data fetching
- **Performance**: Automatic request deduplication saves ~30% API calls

## Compliance
This architecture:
- Enables AIPM to detect React Query patterns
- Supports work items for API integration
- Allows tracking of frontend data flow optimization tasks
