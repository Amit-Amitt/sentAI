import axios, { AxiosError } from "axios";

export interface ApiErrorResponse {
  success: boolean;
  error: string;
  code: string;
  details?: any;
}

const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const axiosInstance = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptor to normalize error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    let message = "An unexpected network error occurred.";
    let code = "NETWORK_ERROR";
    let details: any = null;

    if (error.response) {
      const data = error.response.data as any;
      if (data && typeof data === "object") {
        message = data.error || data.detail || message;
        code = data.code || `HTTP_${error.response.status}`;
        details = data.details || null;

        // Map FastAPI Pydantic validation errors
        if (error.response.status === 422 && Array.isArray(data.detail)) {
          message = "Input validation failed.";
          code = "VALIDATION_ERROR";
          details = data.detail;
        }
      } else {
        message = `Request failed with status code ${error.response.status}`;
      }
    } else if (error.request) {
      message = "No response received from Sentinel AI core services.";
      code = "NO_RESPONSE";
    } else {
      message = error.message || message;
    }

    const normalizedError: ApiErrorResponse = {
      success: false,
      error: message,
      code,
      details,
    };

    return Promise.reject(normalizedError);
  }
);
