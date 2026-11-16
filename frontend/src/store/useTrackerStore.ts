import { create } from 'zustand';
import type { Actividad } from '@/types';

interface TrackerState {
  activeActivity: Actividad | null;
  elapsedSeconds: number;
  setActiveActivity: (activity: Actividad | null) => void;
  setElapsedSeconds: (seconds: number) => void;
  incrementElapsed: () => void;
  resetTracker: () => void;
}

export const useTrackerStore = create<TrackerState>((set) => ({
  activeActivity: null,
  elapsedSeconds: 0,

  setActiveActivity: (activity) => set({ activeActivity: activity }),
  setElapsedSeconds: (seconds) => set({ elapsedSeconds: seconds }),
  incrementElapsed: () =>
    set((state) => ({ elapsedSeconds: state.elapsedSeconds + 1 })),
  resetTracker: () => set({ activeActivity: null, elapsedSeconds: 0 }),
}));
