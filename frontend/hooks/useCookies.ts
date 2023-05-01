import { useState, useEffect } from 'react';
import { setCookie, getCookie } from 'cookies-next';

const useCookies = <T>( key: string, defaultValue: T, useJSON: boolean = false) => {
  // Get value
  const [value, setValue] = useState(() => {
    const cookieValue = getCookie(key)?.toString() ?? "";
    if (cookieValue == null || cookieValue === '') {
      return defaultValue;
    }
    return useJSON ? JSON.parse(cookieValue) : cookieValue;
  });

  // Set value
  useEffect(() => {
    setCookie(key, useJSON ? JSON.stringify(value) : value, { maxAge: 60 * 60 * 24 });
  }, [key, value]);

  return [value, setValue] as const;
}

export default useCookies;
