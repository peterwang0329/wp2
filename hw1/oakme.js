import { Application } from "https://deno.land/x/oak/mod.ts";

const app = new Application();

app.use((ctx) => {
  console.log('url=', ctx.request.url)
  let pathname = ctx.request.url.pathname
  if(pathname == '/name'){
    ctx.response.body = "TAT"
  }else if(pathname == '/age'){
    ctx.response.body = "mUm"
  }
  else if(pathname == '/gender'){
    ctx.response.body = "おとこだ！"
  }
  else {
    ctx.response.state = 404
  }
});

console.log('start at : http://127.0.0.1:8000')
await app.listen({ port: 8000 })
