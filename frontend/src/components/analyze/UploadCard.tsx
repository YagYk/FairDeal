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
        <Card className="border-white/5 bg-white/5 backdrop-blur-xl">
            <CardContent className="p-8">
                {!selectedFile ? (
                    <div
                        {...getRootProps()}
                        className={cn(
                            'group relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-12 transition-all cursor-pointer',
                            isDragActive
                                ? 'border-gold bg-gold/5'
                                : 'border-white/10 hover:border-gold/30 hover:bg-white/5'
                        )}
                    >
                        <input {...getInputProps()} />
                        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white/5 text-slate-500 group-hover:text-gold border border-white/10 group-hover:border-gold/30 group-hover:scale-110 transition-all">
                            <Upload className="h-8 w-8" />
                        </div>
                        <h3 className="text-lg font-bold text-white">Upload your contract</h3>
                        <p className="mt-2 text-center text-sm text-slate-500">
                            Drag and drop your offer letter or employment contract.<br />
                            <span className="font-medium text-slate-300">PDF or DOCX (max 10MB)</span>
                        </p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        <div className="flex items-center justify-between rounded-xl border border-gold/20 bg-gold/5 p-4">
                            <div className="flex items-center space-x-4">
                                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gold/20 text-gold border border-gold/30">
                                    <FileText className="h-6 w-6" />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-white">{selectedFile.name}</p>
                                    <p className="text-xs text-slate-500">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                                </div>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => onFileSelect(null)}
                                disabled={isAnalyzing}
                                className="text-slate-400 hover:text-red-400"
                            >
                                <X className="h-5 w-5" />
                            </Button>
                        </div>

                        <div className="flex flex-col items-center space-y-4">
                            <button
                                className="w-full btn-primary h-12 text-base font-bold flex items-center justify-center"
                                onClick={onAnalyze}
                                disabled={isAnalyzing}
                            >
                                {isAnalyzing ? 'Analyzing...' : 'Analyze Contract'}
                            </button>
                            <div className="flex items-center space-x-2 text-xs text-slate-500">
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
