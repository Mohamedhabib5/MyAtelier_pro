import { useEffect, useMemo, useRef, useState } from 'react';

import { useAuth } from '../../features/auth/AuthProvider';
import { getMyGridPreference, setMyGridPreference } from '../../features/users/api';
import type { AgGridPreferenceState } from './types';

type LocalEnvelope = {
  state: AgGridPreferenceState;
  savedAt: number;
};

function buildDefaultState(): AgGridPreferenceState {
  return {
    pageSize: 10,
  };
}

function normalizeState(raw: Partial<AgGridPreferenceState>, defaults: AgGridPreferenceState): AgGridPreferenceState {
  return {
    columnState: raw.columnState,
    filterModel: raw.filterModel,
    pageSize: raw.pageSize && raw.pageSize > 0 ? raw.pageSize : defaults.pageSize,
  };
}

function loadLocalPreference(storageKey: string, defaults: AgGridPreferenceState): LocalEnvelope {
  if (typeof window === 'undefined') {
    return { state: defaults, savedAt: 0 };
  }
  try {
    const raw = window.localStorage.getItem(storageKey);
    if (!raw) {
      return { state: defaults, savedAt: 0 };
    }
    const parsed = JSON.parse(raw) as Partial<LocalEnvelope & AgGridPreferenceState>;
    if (parsed.state && typeof parsed.state === 'object') {
      return {
        state: normalizeState(parsed.state as Partial<AgGridPreferenceState>, defaults),
        savedAt: typeof parsed.savedAt === 'number' ? parsed.savedAt : 0,
      };
    }
    return {
      state: normalizeState(parsed as Partial<AgGridPreferenceState>, defaults),
      savedAt: 0,
    };
  } catch {
    return { state: defaults, savedAt: 0 };
  }
}

export function useAgGridPreferences(storageKey: string) {
  const { user } = useAuth();
  const defaults = useMemo(() => buildDefaultState(), []);
  const userScopedKey = useMemo(() => `${storageKey}:${user?.id ?? 'guest'}`, [storageKey, user?.id]);
  const [state, setState] = useState<AgGridPreferenceState>(defaults);
  const [hydrated, setHydrated] = useState(false);
  const lastSyncedSignatureRef = useRef<string | null>(null);

  useEffect(() => {
    const local = loadLocalPreference(userScopedKey, defaults);
    setState(local.state);
    setHydrated(!user);
    if (!user) {
      lastSyncedSignatureRef.current = null;
      return;
    }

    let cancelled = false;
    void getMyGridPreference(storageKey)
      .then((remote) => {
        if (cancelled) return;
        const remoteSavedAt = remote.updatedAt ? Date.parse(remote.updatedAt) : 0;
        const pickRemote = remoteSavedAt >= local.savedAt;
        const nextState = pickRemote ? normalizeState(remote.state, defaults) : local.state;
        setState(nextState);
        lastSyncedSignatureRef.current = pickRemote ? JSON.stringify(nextState) : null;
        setHydrated(true);
      })
      .catch(() => {
        if (cancelled) return;
        lastSyncedSignatureRef.current = null;
        setHydrated(true);
      });

    return () => {
      cancelled = true;
    };
  }, [defaults, storageKey, user, userScopedKey]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const envelope: LocalEnvelope = { state, savedAt: Date.now() };
    window.localStorage.setItem(userScopedKey, JSON.stringify(envelope));
  }, [state, userScopedKey]);

  useEffect(() => {
    if (!user || !hydrated) return;
    const signature = JSON.stringify(state);
    if (signature === lastSyncedSignatureRef.current) return;

    const timer = window.setTimeout(() => {
      void setMyGridPreference(storageKey, state)
        .then(() => {
          lastSyncedSignatureRef.current = signature;
        })
        .catch(() => {
          // Keep local fallback; remote persistence is best-effort from UX perspective.
        });
    }, 350);
    return () => window.clearTimeout(timer);
  }, [hydrated, state, storageKey, user]);

  return { state, setState, defaults };
}
