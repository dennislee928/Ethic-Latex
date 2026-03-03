---
paths: "**/*.ts", "**/*.tsx", "**/table*.ts", "**/data-table*.ts"
---

# TanStack Table v8 Corrections

Claude's training may reference React Table v7. This project uses **TanStack Table v8**.

## Package Name Change

```bash
# ❌ Old package (v7)
npm install react-table

# ✅ New package (v8)
npm install @tanstack/react-table
```

## Hook Changes

```typescript
/* ❌ v7 useTable hook */
import { useTable, useSortBy, usePagination } from 'react-table'
const { getTableProps, getTableBodyProps, rows } = useTable(
  { columns, data },
  useSortBy,
  usePagination
)

/* ✅ v8 useReactTable */
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
} from '@tanstack/react-table'

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})
```

## Column Definitions

```typescript
/* ❌ v7 columns */
const columns = [
  { Header: 'Name', accessor: 'name' },
  { Header: 'Age', accessor: 'age' },
]

/* ✅ v8 columns with columnHelper */
import { createColumnHelper } from '@tanstack/react-table'

const columnHelper = createColumnHelper<Person>()
const columns = [
  columnHelper.accessor('name', {
    header: 'Name',
    cell: (info) => info.getValue(),
  }),
  columnHelper.accessor('age', {
    header: 'Age',
  }),
]
```

## Rendering Table

```typescript
/* ❌ v7 rendering */
<table {...getTableProps()}>
  <tbody {...getTableBodyProps()}>
    {rows.map(row => (
      <tr {...row.getRowProps()}>
        {row.cells.map(cell => (
          <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
        ))}
      </tr>
    ))}
  </tbody>
</table>

/* ✅ v8 rendering */
<table>
  <tbody>
    {table.getRowModel().rows.map((row) => (
      <tr key={row.id}>
        {row.getVisibleCells().map((cell) => (
          <td key={cell.id}>
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </td>
        ))}
      </tr>
    ))}
  </tbody>
</table>
```

## Sorting State

```typescript
/* ❌ v7 sorting */
const { setSortBy } = useTable(...)

/* ✅ v8 sorting state */
const [sorting, setSorting] = useState<SortingState>([])
const table = useReactTable({
  state: { sorting },
  onSortingChange: setSorting,
  getSortedRowModel: getSortedRowModel(),
})
```

## Pagination

```typescript
/* ❌ v7 pagination */
const { pageIndex, pageSize, gotoPage } = useTable(...)

/* ✅ v8 pagination */
const [pagination, setPagination] = useState<PaginationState>({
  pageIndex: 0,
  pageSize: 10,
})
const table = useReactTable({
  state: { pagination },
  onPaginationChange: setPagination,
  getPaginationRowModel: getPaginationRowModel(),
})

// Navigation
table.setPageIndex(0)
table.nextPage()
table.previousPage()
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `npm install react-table` | `npm install @tanstack/react-table` |
| `useTable` | `useReactTable` |
| `Header: 'Name'` | `header: 'Name'` (lowercase) |
| `accessor: 'name'` | `columnHelper.accessor('name', {...})` |
| `getTableProps()` | Direct JSX (no spread props needed) |
| `row.cells` | `row.getVisibleCells()` |
| `cell.render('Cell')` | `flexRender(cell.column.columnDef.cell, cell.getContext())` |
