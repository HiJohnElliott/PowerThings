def Plog(heading: str, **kwargs) -> str:
    heading: str = f"\n\n{heading.upper():-^60}\n"
    body: str = heading
    for k, arg in kwargs.items():
        body += f"\t{k.replace("_", " ")}: {arg}\n"
    body += f"{'-' * 60}\n"
    return body