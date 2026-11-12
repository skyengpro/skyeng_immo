import { useNavigate } from 'react-router';
import { useAppState } from '@/app/AppStateContext';
import * as api from '@/data/api';

export function useSignOut() {
  const { setUser } = useAppState();
  const navigate = useNavigate();
  return async () => {
    try {
      await api.logout();
    } catch {
      // Signed out locally anyway; the server session ends with its cookie.
    }
    setUser(null);
    navigate('/connexion');
  };
}
