import React, { useState, useMemo } from 'react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { MessageSquare, AlertTriangle, Lightbulb, Info, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';

interface Annotation {
    tag: string;
    content: string;
    tooltip?: string;
    reasoning: string;
    suggestion?: string;
    position: { start: number; end: number };
    source_name?: string;
    source_link?: string;
}

interface DocumentReviewerProps {
    content: string;
    annotations: Annotation[];
}

interface HighlightMatch {
    start: number;
    end: number;
    annotation: Annotation;
}

export const DocumentReviewer: React.FC<DocumentReviewerProps> = ({ content, annotations }) => {
    const [selectedAnnotation, setSelectedAnnotation] = useState<Annotation | null>(null);
    const [showAllAnnotations, setShowAllAnnotations] = useState(false);

    const getTagColor = (tag: string) => {
        switch (tag) {
            case 'PLAGIARISED':
            case 'REDUNDANT CONTENT': return 'bg-destructive/20 text-destructive border-destructive/30';
            case 'SOUNDS LIKE AI GENERATED': return 'bg-orange-500/20 text-orange-500 border-orange-500/30';
            case 'WEAK ARGUMENT': return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30';
            case 'MISSING CITATION': return 'bg-amber-500/20 text-amber-600 border-amber-500/30';
            case 'UNCLEAR CLAIM': return 'bg-yellow-600/20 text-yellow-600 border-yellow-600/30';
            case 'STRONG INSIGHT': return 'bg-green-500/20 text-green-500 border-green-500/30';
            case 'NOVEL CONTRIBUTION': return 'bg-primary/20 text-primary border-primary/30';
            default: return 'bg-secondary/20 text-secondary border-secondary/30';
        }
    };

    const getTagBgOnly = (tag: string) => {
        switch (tag) {
            case 'PLAGIARISED':
            case 'REDUNDANT CONTENT': return 'bg-destructive/15';
            case 'SOUNDS LIKE AI GENERATED': return 'bg-orange-500/15';
            case 'WEAK ARGUMENT': return 'bg-yellow-500/15';
            case 'MISSING CITATION': return 'bg-amber-500/15';
            case 'UNCLEAR CLAIM': return 'bg-yellow-600/15';
            case 'STRONG INSIGHT': return 'bg-green-500/15';
            case 'NOVEL CONTRIBUTION': return 'bg-primary/15';
            default: return 'bg-secondary/15';
        }
    };

    const getTagIcon = (tag: string) => {
        switch (tag) {
            case 'PLAGIARISED':
            case 'REDUNDANT CONTENT':
            case 'SOUNDS LIKE AI GENERATED': return <AlertTriangle className="h-3 w-3 mr-1" />;
            case 'MISSING CITATION':
            case 'UNCLEAR CLAIM': return <BookOpen className="h-3 w-3 mr-1" />;
            case 'STRONG INSIGHT':
            case 'NOVEL CONTRIBUTION': return <Lightbulb className="h-3 w-3 mr-1" />;
            default: return <Info className="h-3 w-3 mr-1" />;
        }
    };

    // Content-based search: find annotation text within the document content
    const highlights = useMemo<HighlightMatch[]>(() => {
        if (!annotations.length || !content) return [];

        const matches: HighlightMatch[] = [];
        const usedRanges: Array<{ start: number; end: number }> = [];

        for (const anno of annotations) {
            // Search for the annotation's content text within the document
            const searchText = anno.content.trim();
            if (!searchText || searchText.length < 5) continue;

            // Try exact match first
            let idx = content.indexOf(searchText);

            // If exact match fails, try case-insensitive
            if (idx === -1) {
                idx = content.toLowerCase().indexOf(searchText.toLowerCase());
            }

            // If still no match, try first 40 chars (regex may have captured slightly different text)
            if (idx === -1 && searchText.length > 40) {
                const shortSearch = searchText.slice(0, 40);
                idx = content.toLowerCase().indexOf(shortSearch.toLowerCase());
            }

            if (idx === -1) continue;

            const matchEnd = Math.min(idx + searchText.length, content.length);

            // Check for overlap with existing matches
            const overlaps = usedRanges.some(
                r => idx < r.end && matchEnd > r.start
            );
            if (overlaps) continue;

            matches.push({ start: idx, end: matchEnd, annotation: anno });
            usedRanges.push({ start: idx, end: matchEnd });
        }

        // Sort by position
        matches.sort((a, b) => a.start - b.start);
        return matches;
    }, [content, annotations]);

    // Render content with highlights
    const renderContent = () => {
        if (!highlights.length) {
            return <>{content}</>;
        }

        let lastIndex = 0;
        const elements: React.ReactNode[] = [];

        highlights.forEach((match, i) => {
            // Text before this highlight
            if (match.start > lastIndex) {
                elements.push(
                    <span key={`text-${i}`}>{content.substring(lastIndex, match.start)}</span>
                );
            }

            // Highlighted segment
            const highlightedText = content.substring(match.start, match.end);
            const isSelected = selectedAnnotation === match.annotation;

            elements.push(
                <TooltipProvider key={`anno-${i}`} delayDuration={200}>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <mark
                                className={`cursor-pointer no-underline rounded-sm px-0.5 py-0
                                    transition-all duration-300 ease-out
                                    ${getTagBgOnly(match.annotation.tag)}
                                    ${isSelected
                                        ? 'ring-2 ring-primary/50 shadow-lg shadow-primary/10 scale-[1.01]'
                                        : 'hover:ring-1 hover:ring-primary/30 hover:shadow-md'
                                    }
                                `}
                                style={{
                                    borderBottom: `2px solid`,
                                    borderBottomColor: isSelected ? 'hsl(var(--primary))' : 'transparent',
                                }}
                                onClick={() => setSelectedAnnotation(match.annotation)}
                            >
                                {highlightedText}
                            </mark>
                        </TooltipTrigger>
                        <TooltipContent side="top" className="max-w-[320px] p-3 backdrop-blur-md">
                            <div className="flex flex-col gap-1.5">
                                <Badge variant="outline" className={`w-fit text-[10px] ${getTagColor(match.annotation.tag)}`}>
                                    {getTagIcon(match.annotation.tag)}
                                    {match.annotation.tag}
                                </Badge>
                                <p className="text-xs leading-relaxed font-semibold">
                                    {match.annotation.tooltip || "Analysis Insight"}
                                </p>
                                <p className="text-[10px] leading-relaxed opacity-80">
                                    {match.annotation.reasoning.slice(0, 100)}...
                                </p>
                            </div>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            );

            lastIndex = match.end;
        });

        // Remaining text
        if (lastIndex < content.length) {
            elements.push(
                <span key="text-end">{content.substring(lastIndex)}</span>
            );
        }

        return <>{elements}</>;
    };

    // Annotation list for sidebar
    const annotationList = showAllAnnotations ? annotations : annotations.slice(0, 5);

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-[600px]">
            {/* Document Panel */}
            <Card className="lg:col-span-2 overflow-y-auto bg-card/30 backdrop-blur-sm border-border/50 max-h-[75vh]">
                {/* Annotation count bar */}
                {highlights.length > 0 && (
                    <div className="sticky top-0 z-10 bg-card/80 backdrop-blur-md border-b border-border/50 px-6 py-2.5 flex items-center gap-3">
                        <span className="text-xs text-muted-foreground">
                            {highlights.length} annotation{highlights.length !== 1 ? 's' : ''} found
                        </span>
                        <div className="flex gap-1.5 flex-wrap">
                            {[...new Set(annotations.map(a => a.tag))].map(tag => (
                                <Badge key={tag} variant="outline" className={`text-[9px] py-0 ${getTagColor(tag)}`}>
                                    {tag}
                                </Badge>
                            ))}
                        </div>
                    </div>
                )}

                <div className="p-8">
                    <div className="whitespace-pre-wrap font-serif text-[15px] leading-[1.9] text-foreground/90 selection:bg-primary/30">
                        {renderContent()}
                    </div>
                </div>
            </Card>

            {/* Review Panel */}
            <Card className="p-6 border-border/50 bg-card/20 backdrop-blur-md max-h-[75vh] overflow-y-auto">
                <div className="flex items-center gap-2 mb-6 pb-4 border-b border-border">
                    <MessageSquare className="h-5 w-5 text-primary" />
                    <h3 className="font-bold text-lg">Detailed Review</h3>
                </div>

                {selectedAnnotation ? (
                    <div className="flex flex-col gap-4 animate-in fade-in slide-in-from-right-4 duration-300">
                        <Badge variant="outline" className={`w-fit py-1 px-3 ${getTagColor(selectedAnnotation.tag)}`}>
                            {getTagIcon(selectedAnnotation.tag)}
                            {selectedAnnotation.tag}
                        </Badge>

                        <div className="space-y-4">
                            <div>
                                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-2">Segment</h4>
                                <p className="text-foreground italic bg-accent/10 p-3 rounded-md border-l-4 border-primary text-sm leading-relaxed">
                                    &ldquo;{selectedAnnotation.content}&rdquo;
                                </p>
                            </div>

                            <div>
                                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-2">Academic Reasoning</h4>
                                <p className="text-muted-foreground text-sm leading-relaxed whitespace-pre-line">
                                    {selectedAnnotation.reasoning}
                                </p>
                            </div>

                            {selectedAnnotation.source_name && (
                                <div className="bg-destructive/5 p-3 rounded-md border border-destructive/20 animate-in fade-in slide-in-from-bottom-2 duration-300">
                                    <h4 className="text-xs font-bold text-destructive uppercase tracking-widest mb-1">Found in Original Source</h4>
                                    <p className="text-sm font-medium mb-2">{selectedAnnotation.source_name}</p>
                                    <a
                                        href={selectedAnnotation.source_link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-xs text-primary underline hover:text-primary/80 flex items-center gap-1"
                                    >
                                        View original document <Info className="h-3 w-3" />
                                    </a>
                                </div>
                            )}

                            {selectedAnnotation.suggestion && (
                                <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                                    <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-2">Suggestion</h4>
                                    <p className="text-green-400/90 text-sm leading-relaxed bg-green-500/5 p-3 rounded-md border-l-4 border-green-500/30">
                                        {selectedAnnotation.suggestion}
                                    </p>
                                </div>
                            )}

                            <div className="pt-4 mt-4 border-t border-border">
                                <p className="text-[11px] text-muted-foreground">
                                    The evaluation engine detected this pattern with high statistical significance.
                                    Consider addressing this to improve your paper's IEEE-level publication rigor.
                                </p>
                            </div>

                            <button
                                onClick={() => setSelectedAnnotation(null)}
                                className="w-full py-2 text-xs text-muted-foreground hover:text-foreground border border-border/50 rounded-md transition-colors"
                            >
                                Back to list
                            </button>
                        </div>
                    </div>
                ) : (
                    <>
                        {/* Show annotation list when nothing is selected */}
                        {annotations.length > 0 ? (
                            <div className="space-y-3">
                                <p className="text-xs text-muted-foreground mb-4">
                                    Click an annotation below or a highlighted segment in the document.
                                </p>
                                {annotationList.map((anno, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => setSelectedAnnotation(anno)}
                                        className="w-full text-left p-3 rounded-lg border border-border/50 hover:border-primary/40
                                            hover:bg-primary/5 transition-all duration-200 group"
                                    >
                                        <div className="flex items-center gap-2 mb-1.5">
                                            <Badge variant="outline" className={`text-[9px] py-0 ${getTagColor(anno.tag)}`}>
                                                {getTagIcon(anno.tag)}
                                                {anno.tag}
                                            </Badge>
                                        </div>
                                        <p className="text-xs text-muted-foreground truncate group-hover:text-foreground transition-colors">
                                            {anno.content}
                                        </p>
                                    </button>
                                ))}
                                {annotations.length > 5 && (
                                    <button
                                        onClick={() => setShowAllAnnotations(!showAllAnnotations)}
                                        className="w-full text-center text-xs text-primary hover:text-primary/80 py-2 flex items-center justify-center gap-1"
                                    >
                                        {showAllAnnotations ? (
                                            <>Show Less <ChevronUp className="h-3 w-3" /></>
                                        ) : (
                                            <>Show All ({annotations.length}) <ChevronDown className="h-3 w-3" /></>
                                        )}
                                    </button>
                                )}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-[400px] text-center text-muted-foreground">
                                <Info className="h-10 w-10 mb-4 opacity-20" />
                                <p className="max-w-[200px]">No issues detected in this document. High degree of originality!</p>
                            </div>
                        )}
                    </>
                )}
            </Card>
        </div>
    );
};
