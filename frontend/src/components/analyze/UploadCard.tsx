import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, ShieldAlert } from 'lucide-react';
import { Card, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';

interface UploadCardProps {
    onFileSelect: (file: File | null) => void;
    selectedFile: File | null;
    isAnalyzing: boolean;
    onAnalyze: () => void;
}

export const UploadCard = ({ onFileSelect, selectedFile, isAnalyzing, onAnalyze }: UploadCardProps) => {
    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            onFileSelect(acceptedFiles[0]);
        }
    }, [onFileSelect]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        },
        maxFiles: 1,
        disabled: isAnalyzing,
    });

    return (
        <Card className="shadow-premium border-none ring-1 ring-slate-200">
            <CardContent className="p-8">
                {!selectedFile ? (
                    <div
                        {...getRootProps()}
                        className={cn(
                            'group relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-12 transition-all cursor-pointer',
                            isDragActive
                                ? 'border-brand-500 bg-brand-50/50'
                                : 'border-slate-200 hover:border-brand-300 hover:bg-slate-50'
                        )}
                    >
                        <input {...getInputProps()} />
                        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-brand-50 text-brand-600 group-hover:scale-110 transition-transform">
                            <Upload className="h-8 w-8" />
                        </div>
                        <h3 className="text-lg font-bold text-slate-900">Upload your contract</h3>
                        <p className="mt-2 text-center text-sm text-slate-500">
                            Drag and drop your offer letter or employment contract.<br />
                            <span className="font-medium text-slate-700">PDF or DOCX (max 10MB)</span>
                        </p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        <div className="flex items-center justify-between rounded-xl border border-brand-100 bg-brand-50/50 p-4">
                            <div className="flex items-center space-x-4">
                                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-500 text-white">
                                    <FileText className="h-6 w-6" />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-slate-900">{selectedFile.name}</p>
                                    <p className="text-xs text-slate-500">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                                </div>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => onFileSelect(null)}
                                disabled={isAnalyzing}
                                className="text-slate-400 hover:text-red-500"
                            >
                                <X className="h-5 w-5" />
                            </Button>
                        </div>

                        <div className="flex flex-col items-center space-y-4">
                            <Button
                                className="w-full text-base font-bold h-12"
                                size="lg"
                                onClick={onAnalyze}
                                loading={isAnalyzing}
                            >
                                Analyze Contract
                            </Button>
                            <div className="flex items-center space-x-2 text-xs text-slate-400">
                                <ShieldAlert className="h-3.5 w-3.5" />
                                <span>Deterministic extraction. No LLM hallucinations on core numbers.</span>
                            </div>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};
