import type { Order } from "@/lib/types";

type Props = {
  orders: Order[];
  isLoading: boolean;
};

export function CurrentOrdersTable({ orders, isLoading }: Props) {
  return (
    <section className="panel order-book-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Current order book</p>
          <h2>Orders scheduled so far</h2>
        </div>
        <span>{orders.length} orders</span>
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
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-cell">
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
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
