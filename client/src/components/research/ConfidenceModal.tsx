import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import { Shield, ShieldCheck, ShieldAlert, AlertTriangle, ArrowRight } from 'lucide-react';
import { ConfidenceResult } from '@/lib/api';

interface ConfidenceModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirmExit: () => void;
    confidenceResult?: ConfidenceResult;
    confidenceLevel: string;
}

export const ConfidenceModal: React.FC<ConfidenceModalProps> = ({
    isOpen,
    onClose,
    onConfirmExit,
    confidenceResult,
    confidenceLevel,
}) => {
    const level = confidenceResult?.level || confidenceLevel;

    const getLevelColor = (l: string) => {
        switch (l) {
            case 'High': return 'text-green-500';
            case 'Medium': return 'text-yellow-500';
            case 'Low': return 'text-red-500';
            default: return 'text-muted-foreground';
        }
    };

    const getLevelIcon = (l: string) => {
        switch (l) {
            case 'High': return <ShieldCheck className="h-8 w-8 text-green-500" />;
            case 'Medium': return <Shield className="h-8 w-8 text-yellow-500" />;
            case 'Low': return <ShieldAlert className="h-8 w-8 text-red-500" />;
            default: return <AlertTriangle className="h-8 w-8 text-muted-foreground" />;
        }
    };

    const getLevelBg = (l: string) => {
        switch (l) {
            case 'High': return 'bg-green-500/10 border-green-500/30';
            case 'Medium': return 'bg-yellow-500/10 border-yellow-500/30';
            case 'Low': return 'bg-red-500/10 border-red-500/30';
            default: return 'bg-muted/10 border-border';
        }
    };

    const subScores = confidenceResult ? [
        { label: 'Model Certainty', value: confidenceResult.model_certainty, desc: 'How confident the AI is in its analysis models' },
        { label: 'Data Completeness', value: confidenceResult.data_completeness, desc: 'Sufficiency of signals extracted from the document' },
        { label: 'Document Clarity', value: confidenceResult.document_clarity, desc: 'How well-structured and clear the document is' },
        { label: 'Signal Consistency', value: confidenceResult.signal_consistency, desc: 'Agreement between different scoring dimensions' },
    ] : [];

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[520px]">
                <DialogHeader>
                    <DialogTitle>AI Confidence Assessment</DialogTitle>
                    <DialogDescription>
                        Before you leave, here's how confident the AI is in this evaluation.
                    </DialogDescription>
                </DialogHeader>

                {/* Confidence Level Badge */}
                <div className={`flex items-center gap-4 p-4 rounded-lg border ${getLevelBg(level)}`}>
                    {getLevelIcon(level)}
                    <div>
                        <p className={`text-xl font-bold ${getLevelColor(level)}`}>
                            {level} Confidence
                        </p>
                        <p className="text-sm text-muted-foreground mt-1">
                            {confidenceResult?.summary || `The AI has ${level.toLowerCase()} confidence in this evaluation.`}
                        </p>
                    </div>
                </div>

                {/* Sub-scores */}
                {subScores.length > 0 && (
                    <div className="space-y-3 mt-2">
                        {subScores.map((score) => (
                            <div key={score.label} className="space-y-1">
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">{score.label}</span>
                                    <span className="font-medium">{score.value}%</span>
                                </div>
                                <div className="h-2 bg-secondary/20 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full transition-all duration-500 ${score.value >= 70 ? 'bg-green-500' :
                                                score.value >= 45 ? 'bg-yellow-500' : 'bg-red-500'
                                            }`}
                                        style={{ width: `${score.value}%` }}
                                    />
                                </div>
                                <p className="text-xs text-muted-foreground">{score.desc}</p>
                            </div>
                        ))}
                    </div>
                )}

                <DialogFooter className="mt-4 gap-2">
                    <Button variant="outline" onClick={onClose}>
                        Stay on Page
                    </Button>
                    <Button onClick={onConfirmExit} className="group">
                        Leave Anyway
                        <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};
