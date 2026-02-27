import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Trophy,
    MapPin,
    Users,
    Briefcase,
    GraduationCap,
    ArrowLeft,
    ShieldCheck,
    Download,
    ChevronRight,
    ExternalLink,
    Target,
    Clock,
    Tag,
    Loader2,
    CheckCircle2,
    FileText,
} from 'lucide-react';
import { Navbar } from '@/components/landing/Navbar';
import { DocumentReviewer } from '@/components/research/DocumentReviewer';
import { ConfidenceModal } from '@/components/research/ConfidenceModal';
import { toast } from 'sonner';
<<<<<<< HEAD
import { apiClient } from '@/lib/api';
=======
import { apiClient, ResearchStatusResponse } from '@/lib/api';
>>>>>>> 76504fc1dfbada5f52fca01e047c169a0a14ac67

// Stagger animation helper
const useStaggeredReveal = (itemCount: number, baseDelay = 100) => {
    const [visibleItems, setVisibleItems] = useState<Set<number>>(new Set());

    useEffect(() => {
        for (let i = 0; i < itemCount; i++) {
            setTimeout(() => {
                setVisibleItems(prev => new Set([...prev, i]));
            }, baseDelay * (i + 1));
        }
    }, [itemCount, baseDelay]);

    return visibleItems;
};

// Animated counter hook
const useAnimatedCounter = (target: number, duration = 1500) => {
    const [current, setCurrent] = useState(0);

    useEffect(() => {
        if (target === 0) return;
        const startTime = Date.now();
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            setCurrent(Math.round(target * eased * 10) / 10);
            if (progress < 1) requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }, [target, duration]);

    return current;
};

export default function ResearchEvaluation() {
    const { analysisId } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState<ResearchStatusResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [showExitModal, setShowExitModal] = useState(false);
    const [downloading, setDownloading] = useState(false);
    const [headerVisible, setHeaderVisible] = useState(false);
    const [cardsVisible, setCardsVisible] = useState(false);
    const [tabsVisible, setTabsVisible] = useState(false);
    const [sidebarVisible, setSidebarVisible] = useState(false);

    // Stagger reveal for dimension scores
    const dimCount = data ? Object.keys(data.score_dimensions).length : 0;
    const visibleDims = useStaggeredReveal(dimCount, 80);

    // Animated score counter
    const animatedScore = useAnimatedCounter(data?.research_score || 0, 2000);

    // Stagger the main sections
    useEffect(() => {
        if (!data) return;
        const timers = [
            setTimeout(() => setHeaderVisible(true), 100),
            setTimeout(() => setCardsVisible(true), 300),
            setTimeout(() => setTabsVisible(true), 600),
            setTimeout(() => setSidebarVisible(true), 500),
        ];
        return () => timers.forEach(clearTimeout);
    }, [data]);

    useEffect(() => {
        if (!analysisId) return;

        const fetchData = async () => {
            try {
                const result = await apiClient.getResearchStatus(analysisId);

                if (result.status === 'processing') {
                    setTimeout(fetchData, 2000);
                    return;
                }

                setData(result);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching analysis:", error);
<<<<<<< HEAD
                toast.error("Failed to load analysis results. Please ensure the backend is running.");
=======
                if ((error as any)?.message?.includes('202')) {
                    setTimeout(fetchData, 2000);
                    return;
                }
                toast.error("Failed to load analysis results.");
>>>>>>> 76504fc1dfbada5f52fca01e047c169a0a14ac67
                setLoading(false);
            }
        };
        fetchData();
    }, [analysisId]);

    const handleExit = () => setShowExitModal(true);
    const confirmExit = () => { setShowExitModal(false); navigate('/'); };

    const handleDownload = useCallback(async () => {
        if (!analysisId || downloading) return;
        setDownloading(true);
        try {
            await apiClient.downloadResearchReport(analysisId);
            toast.success('Report downloaded successfully!');
        } catch (error) {
            console.error('Download error:', error);
            toast.error('Failed to download report. Please try again.');
        } finally {
            setDownloading(false);
        }
    }, [analysisId, downloading]);

    const handleShare = useCallback(() => {
        if (navigator.share) {
            navigator.share({
                title: 'Research Analysis Report',
                text: `Check out this research analysis: Score ${data?.research_score}/100`,
                url: window.location.href,
            }).catch(() => { });
        } else {
            navigator.clipboard.writeText(window.location.href);
            toast.success('Link copied to clipboard!');
        }
    }, [data]);

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="flex flex-col items-center gap-6">
                    <div className="relative">
                        <div className="h-20 w-20 rounded-full border-4 border-primary/20" />
                        <div className="absolute inset-0 h-20 w-20 rounded-full border-4 border-transparent border-t-primary animate-spin" />
                        <FileText className="absolute inset-0 m-auto h-8 w-8 text-primary/60" />
                    </div>
                    <div className="text-center space-y-2">
                        <p className="text-lg font-medium animate-pulse">Running IEEE-Level Evaluation</p>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                            {['Scoring', 'Annotations', 'Opportunities', 'Faculty'].map((step, i) => (
                                <span key={step} className="flex items-center gap-1 animate-pulse" style={{ animationDelay: `${i * 200}ms` }}>
                                    <div className="h-1.5 w-1.5 rounded-full bg-primary/40" />
                                    {step}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-center space-y-4">
                    <p className="text-xl font-semibold text-destructive">Analysis Not Found</p>
                    <p className="text-muted-foreground">The analysis may have expired or the backend may be restarting.</p>
                    <Button onClick={() => navigate('/')}>Back to Home</Button>
                </div>
            </div>
        );
    }

    const paperContent = data.extracted_text || "No document text available.";
    const dimEntries = Object.entries(data.score_dimensions);

    return (
        <div className="min-h-screen bg-background text-foreground selection:bg-primary/30">
            <Navbar />

            <main className="container pt-24 pb-20 px-4 md:px-6">
                {/* Header Section — slides down */}
                <div className={`flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-10 pb-8 border-b border-border/50
                    transition-all duration-700 ease-out ${headerVisible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-6'}`}>
                    <div className="space-y-2">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="-ml-2 text-muted-foreground hover:text-foreground transition-colors"
                            onClick={handleExit}
                        >
                            <ArrowLeft className="mr-2 h-4 w-4" />
                            Exit Review
                        </Button>
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Research Analysis Report</h1>
                        <p className="text-muted-foreground">
                            Analysis ID: <span className="font-mono text-xs bg-secondary/30 px-2 py-0.5 rounded">{analysisId}</span>
                        </p>
                    </div>

                    <div className="flex gap-3">
                        <Button
                            variant="outline"
                            size="sm"
                            className="group"
                            onClick={handleDownload}
                            disabled={downloading}
                        >
                            {downloading ? (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            ) : (
                                <Download className="mr-2 h-4 w-4 transition-transform group-hover:translate-y-0.5" />
                            )}
                            {downloading ? 'Generating...' : 'PDF Report'}
                        </Button>
                    </div>
                </div>

                {/* Dashboard Grid */}
                <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">

                    {/* Left Column: Scoring & Document View */}
                    <div className="xl:col-span-3 space-y-8">

                        {/* Scoring Dashboard — scales in */}
                        <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6
                            transition-all duration-700 ease-out delay-100 ${cardsVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}>

                            {/* Score Card with animated counter */}
                            <Card className="bg-primary/5 border-primary/20 relative overflow-hidden group hover:shadow-lg hover:shadow-primary/5 transition-shadow duration-500">
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-125 group-hover:opacity-20 transition-all duration-500">
                                    <Trophy className="h-16 w-16" />
                                </div>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Quality Score</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-5xl font-black text-primary mb-2 tabular-nums">
                                        {animatedScore}
                                    </div>
                                    <Progress value={animatedScore} className="h-2 transition-all duration-300" />
                                    <p className="text-xs text-muted-foreground mt-3 flex items-center gap-1">
                                        <CheckCircle2 className="h-3 w-3 text-green-500" />
                                        IEEE Rigor: {data.research_score > 75 ? 'Excellent' : data.research_score > 55 ? 'Strong' : 'Needs Improvement'}
                                    </p>
                                </CardContent>
                            </Card>

                            {/* Dimensions with staggered reveal */}
                            <Card className="lg:col-span-2 border-border/50 bg-card/50 backdrop-blur-sm hover:shadow-lg transition-shadow duration-500">
                                <CardHeader className="pb-1 text-xs font-semibold text-muted-foreground uppercase">Evaluation Dimensions</CardHeader>
                                <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-x-10 gap-y-4 py-4">
                                    {dimEntries.map(([key, value], idx) => (
                                        <div
                                            key={key}
                                            className={`space-y-1.5 transition-all duration-500 ease-out
                                                ${visibleDims.has(idx) ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4'}`}
                                        >
                                            <div className="flex justify-between text-sm">
                                                <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                                                <span className="font-medium tabular-nums">{value as number}%</span>
                                            </div>
                                            <div className="h-1.5 bg-secondary/20 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full rounded-full bg-primary transition-all duration-1000 ease-out"
                                                    style={{
                                                        width: visibleDims.has(idx) ? `${value as number}%` : '0%',
                                                        transitionDelay: `${idx * 80}ms`,
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </CardContent>
                            </Card>
                        </div>

                        {/* Main Tabs — slides up */}
                        <div className={`transition-all duration-700 ease-out delay-300
                            ${tabsVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
                            <Tabs defaultValue="document" className="w-full">
                                <TabsList className="grid w-full grid-cols-3 mb-6 bg-secondary/20 p-1">
                                    <TabsTrigger value="document" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-300">
                                        Document Review
                                    </TabsTrigger>
                                    <TabsTrigger value="opportunities" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-300">
                                        Opportunities ({data.top_opportunities.length})
                                    </TabsTrigger>
                                    <TabsTrigger value="faculty" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-300">
                                        Faculty ({data.faculty_recommendations.length})
                                    </TabsTrigger>
                                </TabsList>

                                <TabsContent value="document" className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                                    <DocumentReviewer content={paperContent} annotations={data.annotations} />
                                </TabsContent>

                                <TabsContent value="opportunities" className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {data.top_opportunities.map((opp: any, idx: number) => (
                                            <Card
                                                key={opp.id}
                                                className="hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 group"
                                                style={{ animationDelay: `${idx * 100}ms` }}
                                            >
                                                <CardHeader>
                                                    <div className="flex justify-between items-start">
                                                        <div className="flex gap-2 flex-wrap mb-2">
                                                            <Badge variant="secondary">{opp.source}</Badge>
                                                            {opp.category && (
                                                                <Badge variant="outline" className="text-xs">
                                                                    <Tag className="h-3 w-3 mr-1" />
                                                                    {opp.category}
                                                                </Badge>
                                                            )}
                                                        </div>
                                                        <div className="flex items-center gap-1 text-xs font-medium text-primary">
                                                            <Target className="h-3 w-3" />
                                                            {opp.relevance_score}% Match
                                                        </div>
                                                    </div>
                                                    <CardTitle className="text-lg group-hover:text-primary transition-colors duration-300">{opp.title}</CardTitle>
                                                    <CardDescription className="text-sm">{opp.description}</CardDescription>
                                                </CardHeader>
                                                <CardContent>
                                                    {opp.why_matched && (
                                                        <p className="text-sm text-muted-foreground italic border-l-2 border-primary/30 pl-3 mb-4">
                                                            {opp.why_matched}
                                                        </p>
                                                    )}
                                                    <div className="flex items-center justify-between mt-2">
                                                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                                            <span className="flex items-center gap-1"><Briefcase className="h-3 w-3" /> Difficulty: {opp.difficulty_score}</span>
                                                            {opp.deadline && (
                                                                <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {opp.deadline}</span>
                                                            )}
                                                        </div>
                                                        <Button size="sm" variant="ghost" className="hover:bg-primary/10 hover:text-primary transition-colors" asChild>
                                                            <a href={opp.link} target="_blank" rel="noopener noreferrer">
                                                                View <ExternalLink className="ml-1 h-3 w-3" />
                                                            </a>
                                                        </Button>
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        ))}
                                    </div>
                                </TabsContent>

                                <TabsContent value="faculty" className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                                    <div className="grid grid-cols-1 gap-6">
                                        {data.faculty_recommendations.map((faculty: any, idx: number) => (
                                            <Card
                                                key={idx}
                                                className="flex flex-col md:flex-row p-0 overflow-hidden bg-card/50 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300"
                                                style={{ animationDelay: `${idx * 120}ms` }}
                                            >
                                                <div className="md:w-1/3 bg-primary/5 p-8 flex flex-col items-center justify-center text-center border-b md:border-b-0 md:border-r border-border group">
                                                    <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                                                        <Users className="h-10 w-10 text-primary" />
                                                    </div>
                                                    <h3 className="text-xl font-bold">{faculty.name}</h3>
                                                    <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1 font-medium">
                                                        <MapPin className="h-3 w-3" /> {faculty.inst}
                                                    </p>
                                                    {faculty.match_score && (
                                                        <Badge className="mt-3 bg-green-500/10 text-green-500 border-green-500/30 hover:bg-green-500/20">
                                                            {faculty.match_score}% Match
                                                        </Badge>
                                                    )}
                                                </div>
                                                <div className="flex-1 p-8">
                                                    <Badge className="mb-4 bg-primary/20 text-primary hover:bg-primary/30 border-none px-3 py-1">{faculty.area}</Badge>
                                                    <div className="space-y-4">
                                                        <div>
                                                            <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-2">Why Recommended?</h4>
                                                            <p className="text-foreground leading-relaxed italic border-l-2 border-primary/30 pl-4">
                                                                "{faculty.why}"
                                                            </p>
                                                        </div>
                                                        <Button size="sm" variant="outline" asChild className="mt-4 group/btn">
                                                            <a href={faculty.link} target="_blank" rel="noopener noreferrer">
                                                                View Lab Profile <ExternalLink className="ml-2 h-3 w-3 transition-transform group-hover/btn:translate-x-0.5" />
                                                            </a>
                                                        </Button>
                                                    </div>
                                                </div>
                                            </Card>
                                        ))}
                                    </div>
                                </TabsContent>
                            </Tabs>
                        </div>
                    </div>

                    {/* Right Column: Confidence & Meta — slides in from right */}
                    <div className={`space-y-6 transition-all duration-700 ease-out delay-200
                        ${sidebarVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-8'}`}>
                        <Card className="border-primary/20 bg-primary/5 hover:shadow-lg hover:shadow-primary/5 transition-shadow duration-500">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Confidence Level</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className={`text-2xl font-bold flex items-center gap-2 ${data.confidence_level === 'High' ? 'text-green-500' :
                                    data.confidence_level === 'Medium' ? 'text-yellow-500' : 'text-destructive'
                                    }`}>
                                    <ShieldCheck className="h-6 w-6" />
                                    {data.confidence_level}
                                </div>
                                <p className="text-xs text-muted-foreground mt-2 leading-relaxed">
                                    {data.confidence_result?.summary || 'Derived from model certainty, citation coverage, and scientific coherence signals.'}
                                </p>

                                {data.confidence_result && (
                                    <div className="mt-4 space-y-2">
                                        {[
                                            { label: 'Model Certainty', value: data.confidence_result.model_certainty },
                                            { label: 'Data Completeness', value: data.confidence_result.data_completeness },
                                            { label: 'Signal Consistency', value: data.confidence_result.signal_consistency },
                                        ].map((s, idx) => (
                                            <div key={s.label} className="space-y-1">
                                                <div className="flex justify-between text-[10px] text-muted-foreground">
                                                    <span>{s.label}</span>
                                                    <span className="tabular-nums">{s.value}%</span>
                                                </div>
                                                <div className="h-1 bg-secondary/20 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full transition-all duration-1000 ease-out ${s.value >= 70 ? 'bg-green-500' : s.value >= 45 ? 'bg-yellow-500' : 'bg-red-500'
                                                            }`}
                                                        style={{
                                                            width: sidebarVisible ? `${s.value}%` : '0%',
                                                            transitionDelay: `${600 + idx * 150}ms`,
                                                        }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        <Card className="border-border/50 bg-card/30 hover:shadow-md transition-shadow duration-300">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Peer Review Logic</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex items-start gap-3">
                                    <div className="h-6 w-6 rounded-full bg-secondary/20 flex items-center justify-center flex-shrink-0 mt-1">
                                        <GraduationCap className="h-3 w-3 text-secondary" />
                                    </div>
                                    <p className="text-xs text-muted-foreground italic">
                                        "Scoring philosophy aligns with IEEE Publication guidelines. 85+ represents top 0.1% of submissions."
                                    </p>
                                </div>
                                <div className="pt-2">
                                    <p className="text-[10px] text-muted-foreground leading-relaxed border-t border-border pt-4">
                                        This is a human feedback assistant. AI signals are intended to guide refinement, not serve as absolute final judgment.
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </main>

            {/* Exit Confidence Modal */}
            <ConfidenceModal
                isOpen={showExitModal}
                onClose={() => setShowExitModal(false)}
                onConfirmExit={confirmExit}
                confidenceResult={data.confidence_result}
                confidenceLevel={data.confidence_level}
            />
        </div>
    );
}
