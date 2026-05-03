export type LabourRequirement = {
  baler_type: string;
  stage: string;
  sequence_order: number;
  required_hours: number;
};

export type Worker = {
  worker_id: string;
  worker_name: string;
  skill: string;
  hours_per_week: number;
};

export type Order = {
  order_id: string;
  baler_type: string;
  quantity: number;
  priority: number;
  status: string;
  earliest_completion_date: string;
  recommended_promise_date: string;
};

export type TablesResponse = {
  labour_requirements: LabourRequirement[];
  workers: Worker[];
  orders: Order[];
  settings: Record<string, string>;
};

export type ScheduledOperation = {
  order_id: string;
  baler_type: string;
  stage: string;
  scheduled_week: string;
  required_hours: number;
};

export type CapacityUsage = {
  week_start: string;
  stage: string;
  available_hours: number;
  used_hours: number;
  remaining_hours: number;
};

export type ScheduleResult = {
  new_order: {
    order_id: string;
    baler_type: string;
  };
  earliest_completion_date: string;
  recommended_promise_date: string;
  bottleneck_stage: string;
  assumptions: string[];
  schedule: ScheduledOperation[];
  capacity_usage: CapacityUsage[];
};
