import { Slot } from '@radix-ui/react-slot';
import { cva } from 'class-variance-authority';
import clsx from 'clsx';
const styles = cva('button', { variants: { variant: { primary: 'button-primary', secondary: 'button-secondary' } }, defaultVariants: { variant: 'secondary' } });
export function Button({ asChild = false, variant, className, ...props }) {
  const Component = asChild ? Slot : 'button';
  return <Component className={clsx(styles({ variant }), className)} {...props} />;
}
