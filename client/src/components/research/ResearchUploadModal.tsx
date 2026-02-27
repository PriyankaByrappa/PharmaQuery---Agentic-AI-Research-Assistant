import React, { useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Upload, FileText, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api';

interface ResearchUploadModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const ResearchUploadModal: React.FC<ResearchUploadModalProps> = ({ isOpen, onClose }) => {
    const [isUploading, setIsUploading] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const navigate = useNavigate();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            if (selectedFile.type !== 'application/pdf') {
                toast.error('Only PDF files are accepted');
                return;
            }
            setFile(selectedFile);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
        try {
            const data = await apiClient.uploadResearchPaper(file);

            if (!data || !data.analysis_id) {
                console.error('Invalid response from server:', data);
                toast.error('Missing analysis ID. Please try again.');
                setIsUploading(false);
                return;
            }

            toast.success('Paper uploaded successfully! Starting analysis...');

            // Navigate to the evaluation page with the analysis ID
            setTimeout(() => {
                setIsUploading(false);
                onClose();
                navigate(`/research/evaluation/${data.analysis_id}`);
            }, 1000);
        } catch (error) {
            console.error('Upload error:', error);
            toast.error('Failed to upload paper. Please ensure the backend is running.');
            setIsUploading(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>Upload Research Paper</DialogTitle>
                    <DialogDescription>
                        Upload your research paper in PDF format for IEEE-level evaluation and opportunity discovery.
                    </DialogDescription>
                </DialogHeader>

                <div className="flex flex-col items-center justify-center py-10 border-2 border-dashed border-border rounded-lg bg-card/50 hover:bg-card/80 transition-colors cursor-pointer relative group">
                    <input
                        type="file"
                        accept=".pdf"
                        className="absolute inset-0 opacity-0 cursor-pointer"
                        onChange={handleFileChange}
                        disabled={isUploading}
                    />

                    <div className="flex flex-col items-center gap-4 text-center px-4">
                        {file ? (
                            <>
                                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                                    <FileText className="h-6 w-6 text-primary" />
                                </div>
                                <div>
                                    <p className="font-medium text-foreground">{file.name}</p>
                                    <p className="text-sm text-muted-foreground">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="h-12 w-12 rounded-full bg-secondary/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <Upload className="h-6 w-6 text-secondary" />
                                </div>
                                <div>
                                    <p className="font-medium text-foreground">Click or drag & drop to upload</p>
                                    <p className="text-sm text-muted-foreground">Accepted format: PDF only</p>
                                </div>
                            </>
                        )}
                    </div>
                </div>

                <DialogFooter className="mt-6">
                    <Button variant="outline" onClick={onClose} disabled={isUploading}>
                        Cancel
                    </Button>
                    <Button onClick={handleUpload} disabled={!file || isUploading} className="min-w-[120px]">
                        {isUploading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Analyzing
                            </>
                        ) : (
                            'Start Scan'
                        )}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};
