import {
  addEdge,
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  type Connection,
  type Edge,
  type Node,
  ReactFlow,
  useEdgesState,
  useNodesState
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect } from "react";
import type { Plan, TaskNode } from "../types/domain";
import { StatusBadge } from "./StatusBadge";

interface DagCanvasProps {
  plan: Plan;
  selectedTaskId: string | null;
  onSelectTask: (task: TaskNode | null) => void;
  onConnect: (fromTaskId: string, toTaskId: string) => void;
  onDeleteDependency: (dependencyId: string) => void;
  onMoveTask: (taskId: string, x: number, y: number) => void;
}

const statusBorder: Record<string, string> = {
  SUCCEEDED: "#d5ff5b",
  RUNNING: "#67e8f9",
  VERIFYING: "#67e8f9",
  FAILED: "#ff6b35",
  BLOCKED: "#ff6b35",
  AWAITING_REVIEW: "#fde68a",
  NEEDS_HUMAN: "#fde68a"
};

function nodeForTask(task: TaskNode, selected: boolean): Node {
  return {
    id: task.id,
    position: { x: task.position_x, y: task.position_y },
    data: { task },
    selected,
    type: "task"
  };
}

function TaskNodeCard({ data, selected }: { data: { task: TaskNode }; selected: boolean }) {
  const task = data.task;
  return (
    <div
      className={`min-h-[118px] w-[260px] border bg-[#171b16]/95 p-3 shadow-[0_18px_40px_rgba(0,0,0,0.35)] ${selected ? "ring-2 ring-limewire" : ""}`}
      style={{ borderColor: statusBorder[task.status] ?? "rgba(141,154,140,0.32)" }}
    >
      <div className="mb-3 flex items-start justify-between gap-2">
        <div className="font-display text-base font-semibold leading-tight text-ink">{task.title}</div>
        <div className="font-mono text-[10px] text-steel">{task.risk_level}</div>
      </div>
      <p className="line-clamp-2 text-xs leading-5 text-steel">{task.description}</p>
      <div className="mt-3 flex items-center justify-between gap-2">
        <StatusBadge status={task.status} />
        <span className="font-mono text-[10px] uppercase text-steel">{task.required_autonomy_level}</span>
      </div>
    </div>
  );
}

const nodeTypes = { task: TaskNodeCard };

export function DagCanvas({ plan, selectedTaskId, onSelectTask, onConnect, onDeleteDependency, onMoveTask }: DagCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  useEffect(() => {
    setNodes(plan.tasks.map((task) => nodeForTask(task, task.id === selectedTaskId)));
    setEdges(
      plan.dependencies.map((dep) => ({
        id: dep.id,
        source: dep.from_task_id,
        target: dep.to_task_id,
        animated: true,
        style: { stroke: "#8d9a8c", strokeWidth: 1.5 }
      }))
    );
  }, [plan, selectedTaskId, setEdges, setNodes]);

  const handleConnect = (connection: Connection) => {
    if (connection.source && connection.target) {
      setEdges((current) => addEdge(connection, current));
      onConnect(connection.source, connection.target);
    }
  };

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={handleConnect}
      onEdgeClick={(_, edge) => onDeleteDependency(edge.id)}
      onNodeClick={(_, node) => onSelectTask(plan.tasks.find((task) => task.id === node.id) ?? null)}
      onPaneClick={() => onSelectTask(null)}
      onNodeDragStop={(_, node) => onMoveTask(node.id, node.position.x, node.position.y)}
      fitView
      className="loom-flow"
    >
      <Background color="#2b3329" gap={24} size={1} variant={BackgroundVariant.Lines} />
      <MiniMap pannable zoomable nodeColor={(node) => statusBorder[(node.data as { task: TaskNode }).task.status] ?? "#8d9a8c"} />
      <Controls showInteractive={false} />
    </ReactFlow>
  );
}
