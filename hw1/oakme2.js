import { Application } from "https://deno.land/x/oak/mod.ts";

const app = new Application();

app.use((ctx) => {
  console.log('url=', ctx.request.url)
  let pathname = ctx.request.url.pathname
  if(pathname == '/'){
    ctx.response.body =
    `
    <html>
    <body>
    <h1>自我介紹網站</h1>
    <ol>
    <h4><a href="/name">姓名</a></h4>
    <h4><a href="/age">年齡</a></h4>
    <h4><a href="/gender">性別</a></h4>
    </ol>
    </body>
    </html>
    `
  }
  else if(pathname == '/name'){
    ctx.response.body =
    `
    <html>
    <body>
    <h2><a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">TAT<a></h2>
    <ol>
    <h4><a href="/">返回</a></h4>
    </ol>
    </body>
    </html>
    `
  }else if(pathname == '/age'){
    ctx.response.body =
    `
    <html>
    <body>
    <h2><a href="https://www.youtube.com/watch?v=hq_8F4lfRBk">nUn<a></h2>
    <ol>
    <h4><a href="/">返回</a></h4>
    </ol>
    </body>
    </html>
    `
  }
  else if(pathname == '/gender'){
    ctx.response.body =
    `
    <html>
    <body>
    <h2><a href="https://www.youtube.com/watch?v=jH-7BpVbUIs">おとこだよ！<a></h2>
    <ol>
    <h4><a href="/">返回</a></h4>
    </ol>
    </body>
    </html>
    `
  }
  else {
    ctx.response.state = 404
  }
});

console.log('start at : http://127.0.0.1:8000')
await app.listen({ port: 8000 })
