export const getApiBase = () => {
  const envBase = typeof process !== 'undefined' && process.env?.REACT_APP_API_URL
    ? process.env.REACT_APP_API_URL
    : (typeof window !== 'undefined' && window.REACT_APP_API_URL) || '';

  return envBase.replace(/\/$/, '');
};
