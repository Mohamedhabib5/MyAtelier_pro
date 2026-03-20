import createCache from "@emotion/cache";
import { prefixer } from "stylis";
import rtlPlugin from "stylis-plugin-rtl";

const rtlCache = createCache({
  key: "muirtl",
  stylisPlugins: [prefixer, rtlPlugin],
});

const ltrCache = createCache({
  key: 'muiltr',
  stylisPlugins: [prefixer],
});

export function getEmotionCache(direction: 'rtl' | 'ltr') {
  return direction === 'rtl' ? rtlCache : ltrCache;
}
