def Plog(heading: str, **kwargs) -> str:
    heading: str = f"\n\n{heading.upper():-^60}\n"
    body: str = heading
    for k, arg in kwargs.items():
        body += f"\t{k.replace("_", " ")}: {arg}\n"
    body += f"{'-' * 60}\n"
    return body


if __name__ == "__main__":
    head = "This is a big heading"
    
    print(
        Plog(
            heading = head,
            Name_goes_here = "John",
            Role = "stud",
            Born = "Nov. 1984",
            Cock = "8============================================D"
        )
    )

    print(len("8============================================D"))