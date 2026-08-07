import * as React from "react"
import { cn } from "@/lib/utils"

interface TabsProps extends React.ComponentProps<"div"> {
  defaultValue: string
  value?: string
  onValueChange?: (value: string) => void
}
interface TabsListProps extends React.ComponentProps<"div"> {}
interface TabsTriggerProps extends React.ComponentProps<"button"> { value: string }
interface TabsContentProps extends React.ComponentProps<"div"> { value: string }

const TabsContext = React.createContext<{ value: string; onValueChange?: (v: string) => void }>({ value: "" })

function Tabs({ defaultValue, value, onValueChange, children, className, ...props }: TabsProps) {
  const [internalValue] = React.useState(defaultValue)
  const currentValue = value ?? internalValue
  return (
    <TabsContext.Provider value={{ value: currentValue, onValueChange }}>
      <div data-slot="tabs" className={cn("flex flex-col gap-2", className)} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  )
}
function TabsList({ className, ...props }: TabsListProps) {
  return (
    <div
      data-slot="tabs-list"
      className={cn("bg-muted text-muted-foreground inline-flex h-9 w-fit items-center justify-center rounded-lg p-[3px] gap-0.5", className)}
      {...props}
    />
  )
}
function TabsTrigger({ value, className, ...props }: TabsTriggerProps) {
  const ctx = React.useContext(TabsContext)
  const active = ctx.value === value
  return (
    <button
      data-slot="tabs-trigger"
      data-state={active ? "active" : "inactive"}
      onClick={() => ctx.onValueChange?.(value)}
      className={cn(
        "inline-flex items-center justify-center gap-1.5 whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50",
        active ? "bg-background text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground",
        className
      )}
      {...props}
    />
  )
}
function TabsContent({ value, className, ...props }: TabsContentProps) {
  const ctx = React.useContext(TabsContext)
  if (ctx.value !== value) return null
  return (
    <div
      data-slot="tabs-content"
      data-state={ctx.value === value ? "active" : "inactive"}
      className={cn("mt-2 focus-visible:outline-none", className)}
      {...props}
    />
  )
}

export { Tabs, TabsList, TabsTrigger, TabsContent }
