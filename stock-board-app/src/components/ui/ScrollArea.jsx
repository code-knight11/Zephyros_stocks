export function ScrollArea({ className, children, ...props }) {
    return (
      <div className={`relative overflow-auto ${className}`} {...props}>
        {children}
      </div>
    );
  }