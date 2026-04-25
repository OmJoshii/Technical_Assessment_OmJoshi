# Order & Inventory System — The AI Foundry Technical Assessment

## How to Run
**Requirements:** Python 3.9+

```bash
python inventory_system.py
```

No external dependencies required — uses only the Python standard library.
---

## Section 1 — Approach & Design Decisions

### Overall Design

The core logic is a single function `process_order(products, order)` that takes a product list and a customer order, validates everything, and returns a structured success or error response.

The most important design decision is: **validate first, mutate last.** Stock is only deducted after every single check passes. This prevents partial updates — if item 3 of 5 fails, nothing has been touched yet.

### Step-by-Step Flow

1. Check if the order has any items at all — return an error immediately if not.
2. Convert the product list into a dictionary (`product_id → product`) for fast O(1) lookups.
3. Merge duplicate product IDs in the order by combining their quantities.
4. Validate each item — invalid quantity, product not found, insufficient stock.
5. If all checks pass, deduct stock and return a success response with updated inventory.

### Edge Cases Handled

| # | Edge Case | How It's Handled |
|---|---|---|
| 1 | Empty order | Checked first — returns error before any other logic |
| 2 | Duplicate product entries | Quantities merged before validation so total demand is checked correctly |
| 3 | Invalid quantity (0 or negative) | Rejected with a clear message |
| 4 | Product ID not in inventory | Returns error with the unknown product ID |
| 5 | Requested quantity exceeds stock | Returns error showing both requested and available quantities |

---

## Section 1 — Bonus: Scalability Thinking

### How would you handle 10,000 orders per minute?

The current solution runs in memory and processes one order at a time. At 10,000 orders/min that breaks down quickly. Here is how I would redesign it:

**1. Wrap it in a REST API (e.g. FastAPI)**
Turn `process_order` into an HTTP endpoint. Each request is stateless, which makes it easy to scale horizontally.

**2. Move inventory to a database**
In-memory dicts don't survive restarts and can't be shared across multiple server instances. A database like PostgreSQL lets multiple servers read and write the same inventory. Stock deductions must use atomic operations or row-level locking to prevent two orders from claiming the last unit simultaneously.

**3. Add a message queue (e.g. Kafka or RabbitMQ)**
Instead of processing orders synchronously inside the HTTP request, push orders onto a queue and return an "accepted" response immediately. Background workers consume the queue and do the actual processing. This absorbs traffic spikes gracefully.

**4. Horizontal scaling**
Run multiple API server instances behind a load balancer. Since each instance is stateless, scaling out is just a matter of adding more containers.

**5. Cache the product catalogue**
Product names and IDs change rarely. Cache them in Redis so every validation check doesn't hit the database.

---

## Section 2 — Warehouse Allocation

### Current State

| Product | Warehouse A | Warehouse B |
|---|---|---|
| P1 — Shampoo | 5 units | 10 units |
| P2 — Soap | 10 units | 5 units |

### Order Requirements

| Product | Quantity Needed |
|---|---|
| P1 — Shampoo | 8 units |
| P2 — Soap | 6 units |

---

### Question 1 — Exact Allocation Plan

**P1 — Shampoo (8 units needed):**
- Warehouse A only has 5 — cannot fulfil alone.
- Warehouse B has 10 — can fulfil entirely.
- **Ship all 8 units of P1 from Warehouse B.**

**P2 — Soap (6 units needed):**
- Warehouse B only has 5 — cannot fulfil alone.
- Warehouse A has 10 — can fulfil entirely.
- **Ship all 6 units of P2 from Warehouse A.**

**Final Allocation:**

| Warehouse | Ships |
|---|---|
| Warehouse A | P2 — Soap × 6 |
| Warehouse B | P1 — Shampoo × 8 |

**Remaining Stock After Fulfilment:**

| Product | Warehouse A | Warehouse B |
|---|---|---|
| P1 — Shampoo | 5 (unchanged) | 2 |
| P2 — Soap | 4 | 5 (unchanged) |

---

### Question 2 — Strategy: Minimise Shipment Splits

I chose to fulfil each product entirely from one warehouse wherever possible — no product is split across two warehouses.

**Why:**
- Simpler logistics — one pick, one pack, one label per product line.
- Fewer partial delivery issues — if one shipment is delayed, only one product is affected.
- In this case it works out perfectly: each warehouse is the only one that can fully cover one of the two products, so no compromise is needed.

---

### Question 3 — Assumptions

1. **Both warehouses have similar shipping costs and delivery times.** If one were significantly closer, I'd weight allocations toward it.
2. **Shipping cost is per shipment, not per unit.** Two shipments is acceptable.
3. **Stock figures are real-time and accurate.** No other orders are modifying inventory concurrently.
4. **Both products go to the same destination.** If they were going to different locations, each product's warehouse choice would be evaluated independently.
5. **No warehouse has processing backlogs.** Both can ship immediately.

---

## Section 3 — Quantitative & Logical Reasoning

### Q1 — Throughput Calculation

**Given:** 2 seconds per order, 5 orders handled simultaneously.

```
Orders per second = 5 ÷ 2     = 2.5 orders/second
Orders per minute = 2.5 × 60  = 150 orders/minute
```

**The system can process 150 orders per minute.**

---

### Q2 — Overload Scenario at 300 Orders/Minute

The system capacity is 150 orders/minute but 300 are arriving — twice what it can handle.

**What happens:**
- All 5 processing slots are always full. New orders can't be picked up immediately and queue up.
- The queue grows by 150 orders every minute without bound.
- Response times climb continuously as orders wait longer and longer.
- Eventually memory is exhausted and the process crashes, or if there's a queue limit, orders start getting dropped.

**Failure mode: unbounded queue growth → memory exhaustion → crash or order loss.**

---

### Q3 — Improvement: Add More Parallel Workers

**Suggestion:** Increase parallel workers from 5 to 10 (or more).

Doubling the workers doubles throughput from 150 to 300 orders/minute — exactly matching the new load. This is the most direct fix because the bottleneck is concurrency, not the logic itself.

In practice this means running more async workers within a process (for I/O-bound work) or more server instances behind a load balancer (for distributed workloads). It scales linearly with no changes to the core processing logic.

---

*Submitted by Om Joshi — The AI Foundry Internship Technical Assessment*