#!/usr/bin/env python3
"""OSC listener test — verifies mixx-dj-mcp sends correct packets to port 7000."""
import argparse
import asyncio
import time
from pythonosc import dispatcher, osc_server, udp_client

SERVER_PORT = 7000
CLIENT_PORT = 9000  # arbitrary, for bidirectional if needed

RECEIVED = []

def osc_handler(address, *args):
    msg = f"  OSC <- {address} = {args}"
    RECEIVED.append(msg)
    print(msg)

async def listen(timeout=15):
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(osc_handler)

    server = osc_server.AsyncIOOSCUDPServer(
        ("127.0.0.1", SERVER_PORT), disp, asyncio.get_event_loop())
    transport, _ = await server.create_serve_endpoint()
    print(f"OSC listener on port {SERVER_PORT}")
    print("Waiting for mixx-dj-mcp to send packets...")
    print(f"(Run: mixx_daw('resolume_sync', deck=1))")
    print(f"Timeout: {timeout}s\n")

    await asyncio.sleep(timeout)
    transport.close()
    return RECEIVED

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=15, help="Listen duration (s)")
    args = parser.parse_args()

    print(f"=== OSC Bridge Test ===")
    print(f"Listening on 127.0.0.1:{SERVER_PORT}")
    print(f"Timeout: {args.timeout}s\n")

    msgs = asyncio.run(listen(args.timeout))

    print(f"\n=== Results ===")
    print(f"Received {len(msgs)} OSC messages")
    
    required = ["/composition/tempo", "/composition/bpm", "/layer1/opacity"]
    for addr in required:
        found = any(addr in m for m in msgs)
        print(f"  {'✅' if found else '❌'} {addr}")
    
    print(f"\n{'PASS' if all(any(a in m for m in msgs) for a in required) else 'FAIL'}")
