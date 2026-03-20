import axios from 'axios';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
    AnalyzeResponse,
    KBHealth,
    KBStats,
    KBContractMetadata,
    KBContractsResponse,
    KBChunkPreview,
    Context,
    ClauseType,
    EvaluationReport,
} from './types';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 120000, // 2 minutes for LLM processing
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle structured backend errors
        if (error.response?.data?.error) {
            const backendError = error.response.data.error;
            // Throw a new Error with the backend message so React Query displays it
            const enhancedError = new Error(backendError.message || 'Unknown server error');
            (enhancedError as any).code = backendError.code;
            (enhancedError as any).details = backendError.details;
            return Promise.reject(enhancedError);
        }
        // Handle legacy or validation errors (fastapi default 422 structure before our changes)
        if (error.response?.data?.detail) {
            return Promise.reject(new Error(error.response.data.detail));
        }

        return Promise.reject(error);
    }
);

// --- Hooks ---

export const useAnalyzeContract = () => {
    return useMutation({
        mutationFn: async ({ file, context }: { file: File; context: Context }) => {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('context', JSON.stringify(context));
            const { data } = await api.post<AnalyzeResponse>('/api/analyze', formData);
            return data;
        },
    });
};

export const useKBHealth = () => {
    return useQuery({
        queryKey: ['kb', 'health'],
        queryFn: async () => {
            const { data } = await api.get<KBHealth>('/api/kb/health');
            return data;
        },
    });
};

export const useKBStats = () => {
    return useQuery({
        queryKey: ['kb', 'stats'],
        queryFn: async () => {
            const { data } = await api.get<KBStats>('/api/kb/stats');
            return data;
        },
    });
};

export const useKBContracts = (params: { limit: number; offset: number }) => {
    return useQuery({
        queryKey: ['kb', 'contracts', params],
        queryFn: async () => {
            const { data } = await api.get<KBContractsResponse>('/api/kb/contracts', { params });
            return data;
        },
    });
};

export const useKBContract = (contractId: string) => {
    return useQuery({
        queryKey: ['kb', 'contract', contractId],
        queryFn: async () => {
            const { data } = await api.get<KBContractMetadata>(`/api/kb/contracts/${contractId}`);
            return data;
        },
        enabled: !!contractId,
    });
};

export const useKBContractChunks = (contractId: string) => {
    return useQuery({
        queryKey: ['kb', 'contract-chunks', contractId],
        queryFn: async () => {
            const { data } = await api.get<KBChunkPreview[]>(`/api/kb/contracts/${contractId}/chunks`);
            return data;
        },
        enabled: !!contractId,
    });
};

export const useKBSearch = (params: { query: string; clause_type?: ClauseType; top_k?: number }) => {
    return useQuery({
        queryKey: ['kb', 'search', params],
        queryFn: async () => {
            const { data } = await api.get<KBChunkPreview[]>('/api/kb/search', { params });
            return data;
        },
        enabled: !!params.query,
    });
};

// ── Evaluation ──

export const useRunEvaluation = () => {
    return useMutation({
        mutationFn: async () => {
            const { data } = await api.post<EvaluationReport>('/api/evaluate/run');
            return data;
        },
    });
};

export const useEvaluationResults = () => {
    return useQuery({
        queryKey: ['evaluation', 'results'],
        queryFn: async () => {
            const { data } = await api.get<EvaluationReport>('/api/evaluate/results');
            return data;
        },
    });
};

export default api;
