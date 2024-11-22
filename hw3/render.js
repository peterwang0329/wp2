export function layout(user,title, content) {
    return `
    <html>
    <head>
      <title>${user}: ${title}</title>
      <style>
        body {
          padding: 80px;
          font: 16px Helvetica, Arial;
        }
    
        h1 {
          font-size: 2em;
        }
    
        h2 {
          font-size: 1.2em;
        }
    
        #posts {
          margin: 0;
          padding: 0;
        }
    
        #posts li {
          margin: 40px 0;
          padding: 0;
          padding-bottom: 20px;
          border-bottom: 1px solid #eee;
          list-style: none;
        }
    
        #posts li:last-child {
          border-bottom: none;
        }
    
        textarea {
          width: 500px;
          height: 300px;
        }
    
        input[type=text],
        textarea {
          border: 1px solid #eee;
          border-top-color: #ddd;
          border-left-color: #ddd;
          border-radius: 2px;
          padding: 15px;
          font-size: .8em;
        }
    
        input[type=text] {
          width: 500px;
        }
      </style>
    </head>
    <body>
      <section id="content">
      <h1>使用者：${user}</h1>
        ${content}
      </section>
    </body>
    </html>
    `
  }

  export function userList(users) {
    let listHtml = []
    for (let user of users) {
        listHtml.push(`<li><a href="/${user}/">${user}</a></li>`)
    }
    return layout('', 'User List', `<ol>${listHtml.join('\n')}</ol>`)
  }

  export function list(users,posts) {
    let list = []
    for (let post of posts) {
      const formattedDate = new Date(post.Date).toLocaleString(); // 格式化時間
      list.push(`
      <li>
        <h2>${ post.title }</h2>
        <p>Create at: ${formattedDate}<p>
        <p><a href="/${users}/post/${post.id}">Read post</a></p>
      </li>
      `)
    }
    let content = `
    <h1>Posts</h1>
    <p>You have <strong>${posts.length}</strong> posts!</p>
    <p><a href="/${users}/post/new">Create a Post</a></p>
    <ul id="posts">
      ${list.join('\n')} 
    </ul>
    `
    return layout(users,'Posts', content)
  }
  
  export function newPost(user) {
    console.log('user:',user,',Add');
    return layout(user,'New Post', `
    <h1>New Post</h1>
    <p>Create a new post.</p>
    <form action="/${user}/post" method="post">
      <p><input type="text" placeholder="Title" name="title"></p>
      <p><textarea placeholder="Contents" name="body"></textarea></p>
      <p><input type="submit" value="Create"></p>
    </form>
    `)
  }
  
  export function show(user, post) {
    console.log('user=',user,'Show')
    const formattedDate = new Date(post.Date).toLocaleString();
    return layout(user,post.title, `
      <h1>${post.title}</h1>
      <h3>Create at: ${formattedDate}<h3>
      <pre>${post.body}</pre>
    `)
  }
  