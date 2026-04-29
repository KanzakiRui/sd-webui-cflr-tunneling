def preload(parser):
    parser.add_argument(
        "--cloudflared",
        type=str,
        default=None,
        metavar="TOKEN",
        help=(
            "Start Cloudflared tunnel. Provide a token for persistent tunnel mode; "
            "omit to use quick tunnel mode."
        ),
    )
