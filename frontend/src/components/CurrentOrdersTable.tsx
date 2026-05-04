import { Trash2 } from "lucide-react";
import type { Order } from "@/lib/types";

type Props = {
  orders: Order[];
  isLoading: boolean;
  startDate: string;
  isSavingStartDate: boolean;
  deletingOrderId: string | null;
  onStartDateChange: (startDate: string) => void;
  onDeleteOrder: (orderId: string) => void;
};

export function CurrentOrdersTable({
  orders,
  isLoading,
  startDate,
  isSavingStartDate,
  deletingOrderId,
  onStartDateChange,
  onDeleteOrder,
}: Props) {
  return (
    <section className="panel order-book-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Current order book</p>
          <h2>Orders scheduled so far</h2>
        </div>
        <div className="order-book-actions">
          <label>
            <span>Planning start date</span>
            <input
              type="date"
              value={startDate}
              disabled={isSavingStartDate}
              onChange={(event) => onStartDateChange(event.target.value)}
            />
          </label>
          <span>{orders.length} orders</span>
        </div>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Order</th>
              <th>Baler Type</th>
              <th className="numeric">Quantity</th>
              <th className="numeric">Priority</th>
              <th>Completion</th>
              <th>Promise</th>
              <th>Status</th>
              <th aria-label="Actions" />
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan={8} className="empty-cell">
                  {isLoading ? "Loading current orders..." : "No current orders yet."}
                </td>
              </tr>
            ) : (
              orders.map((order) => (
                <tr key={order.order_id}>
                  <td>{order.order_id}</td>
                  <td>{order.baler_type}</td>
                  <td className="numeric">{order.quantity}</td>
                  <td className="numeric">{order.priority}</td>
                  <td>{order.earliest_completion_date || "Not scheduled"}</td>
                  <td>{order.recommended_promise_date || "Not promised"}</td>
                  <td>{order.status}</td>
                  <td className="actions-cell">
                    <button
                      className="icon-button danger-button"
                      onClick={() => onDeleteOrder(order.order_id)}
                      disabled={deletingOrderId === order.order_id}
                      title={`Delete ${order.order_id}`}
                      aria-label={`Delete ${order.order_id}`}
                    >
                      <Trash2 size={16} aria-hidden="true" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
