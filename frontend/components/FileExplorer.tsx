'use client';

import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { FolderTree, File, Folder, ChevronRight } from 'lucide-react';

interface FileNode {
    name: string;
    type: 'file' | 'dir';
    children?: FileNode[];
}

function FileTreeItem({ node, depth = 0 }: { node: FileNode; depth?: number }) {
    const Icon = node.type === 'dir' ? Folder : File;
    const iconColor = node.type === 'dir' ? 'text-amber-400' : 'text-blue-400';

    return (
        <div>
            <div
                className={`flex items-center gap-1.5 py-1 px-2 rounded hover:bg-secondary/30 cursor-pointer transition-colors text-xs`}
                data-depth={depth}
            >
                {node.type === 'dir' && <ChevronRight className="w-3 h-3 text-muted-foreground" />}
                <Icon className={`w-3.5 h-3.5 ${iconColor}`} />
                <span className="text-foreground/80">{node.name}</span>
            </div>
            {node.children?.map((child, i) => (
                <FileTreeItem key={i} node={child} depth={depth + 1} />
            ))}
        </div>
    );
}

export function FileExplorer({ files }: { files?: FileNode[] }) {
    const sampleFiles: FileNode[] = files || [];

    return (
        <Card className="h-full flex flex-col">
            <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-xs">
                    <FolderTree className="w-3.5 h-3.5 text-amber-400" />
                    Files
                </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden p-0">
                <ScrollArea className="h-full pb-4">
                    {sampleFiles.length === 0 ? (
                        <div className="text-center text-muted-foreground text-sm py-8">
                            <FolderTree className="w-8 h-8 mx-auto mb-2 opacity-20" />
                            No files yet
                        </div>
                    ) : (
                        sampleFiles.map((node, i) => <FileTreeItem key={i} node={node} />)
                    )}
                </ScrollArea>
            </CardContent>
        </Card>
    );
}
