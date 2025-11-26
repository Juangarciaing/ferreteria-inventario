export const apiClient = {
  get: () => Promise.resolve({ data: {} }),
  post: () => Promise.resolve({ data: {} }),
  put: () => Promise.resolve({ data: {} }),
  patch: () => Promise.resolve({ data: {} }),
  delete: () => Promise.resolve({ data: {} }),
  interceptors: {
    request: {
      use: () => {},
    },
    response: {
      use: () => {},
    },
  },
};

export const TokenManager = {
  getToken: () => null,
  setToken: () => {},
  removeToken: () => {},
};
