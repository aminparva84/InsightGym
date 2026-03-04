import React, { createContext, useContext } from 'react';

export const LayoutContext = createContext(null);

export const useLayout = () => {
  const ctx = useContext(LayoutContext);
  return ctx; /* may be null if used outside provider */
};
