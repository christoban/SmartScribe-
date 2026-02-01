import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

// Variable pour éviter les appels multiples simultanés au refresh
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

// 🔧 INTERCEPTOR REQUEST : Injecter automatiquement le token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 🔧 INTERCEPTOR RESPONSE : Gérer le refresh automatique sur erreur 401
api.interceptors.response.use(
  (response) => {
    // Si la réponse est OK, on la retourne directement
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Si l'erreur n'est pas 401, on la propage
    if (error.response?.status !== 401) {
      return Promise.reject(error);
    }

    // Si c'est déjà une tentative de refresh qui a échoué, on déconnecte
    if (originalRequest.url === '/auth/refresh-token') {
      // Clear localStorage et redirection vers login
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Si on a déjà tenté de refresh cette requête, on déconnecte
    if (originalRequest._retry) {
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Marquer la requête comme "déjà tentée"
    originalRequest._retry = true;

    // Si un refresh est déjà en cours, on met cette requête en file d'attente
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        })
        .catch(err => {
          return Promise.reject(err);
        });
    }

    // Démarrer le processus de refresh
    isRefreshing = true;

    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
      // Pas de refresh token disponible → déconnexion
      isRefreshing = false;
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    try {
      // Appeler l'endpoint de refresh
      const response = await axios.post(
        'http://localhost:8000/api/v1/auth/refresh-token',
        { refresh_token: refreshToken },
        { headers: { 'Content-Type': 'application/json' } }
      );

      const { access_token, refresh_token: newRefreshToken } = response.data;

      // Stocker les nouveaux tokens
      localStorage.setItem('token', access_token);
      if (newRefreshToken) {
        localStorage.setItem('refresh_token', newRefreshToken);
      }

      // Mettre à jour le header de la requête originale
      originalRequest.headers.Authorization = `Bearer ${access_token}`;

      // Traiter la file d'attente avec le nouveau token
      processQueue(null, access_token);

      // Rejouer la requête originale
      return api(originalRequest);

    } catch (refreshError) {
      // Le refresh a échoué → déconnexion
      processQueue(refreshError, null);
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      return Promise.reject(refreshError);

    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
