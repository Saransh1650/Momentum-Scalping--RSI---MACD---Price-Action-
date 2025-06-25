from datetime import datetime

def log_event(event_type, price, info="", file_path="trade_events.log"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, "a") as f:
        f.write(f"[{timestamp}] {event_type.upper()} @ {price:.2f} | {info}\n")
