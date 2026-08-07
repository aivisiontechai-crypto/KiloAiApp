import * as React from "react"
import { cn } from "@/lib/utils"

interface TableProps extends React.ComponentProps<"table"> {}
interface TableHeaderProps extends React.ComponentProps<"thead"> {}
interface TableBodyProps extends React.ComponentProps<"tbody"> {}
interface TableRowProps extends React.ComponentProps<"tr"> {}
interface TableHeadProps extends React.ComponentProps<"th"> {}
interface TableCellProps extends React.ComponentProps<"td"> {}

function Table({ className, ...props }: TableProps) {
  return (
    <div className="w-full overflow-auto">
      <table data-slot="table" className={cn("w-full caption-bottom text-sm", className)} {...props} />
    </div>
  )
}
function TableHeader({ className, ...props }: TableHeaderProps) {
  return <thead data-slot="table-header" className={cn("[&_tr]:border-b", className)} {...props} />
}
function TableBody({ className, ...props }: TableBodyProps) {
  return <tbody data-slot="table-body" className={cn("[&_tr:last-child]:border-0", className)} {...props} />
}
function TableRow({ className, ...props }: TableRowProps) {
  return <tr data-slot="table-row" className={cn("border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted", className)} {...props} />
}
function TableHead({ className, ...props }: TableHeadProps) {
  return <th data-slot="table-head" className={cn("text-foreground h-10 px-2 text-left align-middle font-medium whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]", className)} {...props} />
}
function TableCell({ className, ...props }: TableCellProps) {
  return <td data-slot="table-cell" className={cn("p-2 align-middle whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]", className)} {...props} />
}

export { Table, TableHeader, TableBody, TableRow, TableHead, TableCell }
