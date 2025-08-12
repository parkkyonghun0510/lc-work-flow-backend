'use client';

import { ReactNode, ElementType } from 'react';

interface KhmerTextProps {
  children: ReactNode;
  className?: string;
  as?: ElementType;
}

export function KhmerText({ children, className = '', as: Component = 'span', ...props }: KhmerTextProps) {
  return (
    <Component 
      className={`font-khmer ${className}`} 
      style={{ fontFamily: 'var(--font-khmer)' }}
      {...props}
    >
      {children}
    </Component>
  );
}

export function EnglishText({ children, className = '', as: Component = 'span', ...props }: KhmerTextProps) {
  return (
    <Component 
      className={`font-sans ${className}`} 
      style={{ fontFamily: 'var(--font-inter)' }}
      {...props}
    >
      {children}
    </Component>
  );
} 