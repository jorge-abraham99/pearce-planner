import unittest
from datetime import date

from app.csv_loader import delete_order, load_labour_requirements, load_orders, load_settings, load_workers, save_orders, update_start_date
from app.scheduler import (
    build_daily_capacity,
    build_daily_stage_limits,
    build_next_order,
    build_weekly_capacity,
    capacity_skill_for_stage,
    get_baler_types,
    schedule_new_order,
)


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.original_orders = load_orders()
        self.original_settings = load_settings()

    def tearDown(self):
        save_orders(self.original_orders)
        update_start_date(date.fromisoformat(self.original_settings["start_date"]))

    def test_baler_types_include_all_demo_products(self):
        self.assertEqual(get_baler_types(load_labour_requirements()), ["HB550", "HB60", "MC32STD", "SC3000"])

    def test_weekly_capacity_is_grouped_by_skill(self):
        self.assertEqual(
            build_weekly_capacity(load_workers()),
            {
                "welding": 135.0,
                "spraying": 85.0,
                "assembling": 120.0,
            },
        )

    def test_daily_capacity_is_hours_per_week_divided_by_five(self):
        self.assertEqual(
            build_daily_capacity(load_workers()),
            {
                "welding": 27.0,
                "spraying": 17.0,
                "assembling": 24.0,
            },
        )
        self.assertEqual(
            build_daily_stage_limits(load_workers()),
            {
                "welding": 10.0,
                "spraying": 9.0,
                "assembling": 8.0,
            },
        )

    def test_pressing_uses_assembling_capacity(self):
        self.assertEqual(capacity_skill_for_stage("press"), "assembling")
        self.assertEqual(capacity_skill_for_stage("welding"), "welding")

    def test_schedule_new_order_returns_proposed_delivery_answer(self):
        result = schedule_new_order("HB550", load_labour_requirements(), load_workers(), [], load_settings())

        self.assertEqual(result["new_order"], {"order_id": "O001", "baler_type": "HB550"})
        self.assertEqual(result["order_to_save"]["status"], "current")
        self.assertEqual(result["order_to_save"]["earliest_completion_date"], "2026-05-09")
        self.assertEqual(result["order_to_save"]["recommended_promise_date"], "2026-05-10")
        self.assertEqual(result["earliest_completion_date"], date(2026, 5, 9))
        self.assertEqual(result["recommended_promise_date"], date(2026, 5, 10))
        self.assertEqual(result["bottleneck_stage"], "welding")
        self.assertEqual(len(result["schedule"]), 9)
        self.assertTrue(all(row["order_id"] == "O001" for row in result["schedule"]))
        self.assertEqual(
            [(row["stage"], row["scheduled_week"], row["required_hours"]) for row in result["schedule"]],
            [
                ("press", date(2026, 5, 3), 3.0),
                ("welding", date(2026, 5, 3), 5.0),
                ("welding", date(2026, 5, 4), 10.0),
                ("welding", date(2026, 5, 5), 10.0),
                ("welding", date(2026, 5, 6), 10.0),
                ("welding", date(2026, 5, 7), 1.0),
                ("spraying", date(2026, 5, 7), 7.0),
                ("assembling", date(2026, 5, 8), 8.0),
                ("assembling", date(2026, 5, 9), 7.0),
            ],
        )

    def test_next_order_uses_current_order_book_sequence(self):
        self.assertEqual(
            build_next_order("HB60", [{"order_id": "O007", "priority": 3}]),
            {
                "order_id": "O008",
                "baler_type": "HB60",
                "quantity": 1,
                "priority": 4,
                "status": "current",
            },
        )

    def test_invalid_baler_type_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown baler type"):
            schedule_new_order(
                "NOPE",
                load_labour_requirements(),
                load_workers(),
                load_orders(),
                load_settings(),
            )

    def test_delete_order_removes_order_from_csv(self):
        save_orders(
            [
                {
                    "order_id": "O001",
                    "baler_type": "HB550",
                    "quantity": 1,
                    "priority": 1,
                    "status": "current",
                    "earliest_completion_date": "2026-05-09",
                    "recommended_promise_date": "2026-05-10",
                }
            ]
        )

        delete_order("O001")

        self.assertEqual(load_orders(), [])

    def test_update_start_date_persists_setting(self):
        update_start_date(date(2026, 5, 20))

        self.assertEqual(load_settings()["start_date"], "2026-05-20")


if __name__ == "__main__":
    unittest.main()
