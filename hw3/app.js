import { Application, Router } from "https://deno.land/x/oak/mod.ts";
import * as render from './render.js'

const posts = {
    peter:[{id:0, title:'aaa', body:'aaaaa', Date:'Thu Mar 16 2024 11:52:13 GMT+0800 (台北標準時間)'}],
    OAO:[{id:1, title:'bbb', body:'bbbbb', Date:'Thu Apr 21 2024 15:44:30 GMT+0800 (台北標準時間)'}]
};

const router = new Router();

router.get('/', userlist)
    .get('/:user/', list)
    .get('/:user/post/new', add)
    .get('/:user/post/:id', show)
    .post('/:user/post', create);

const app = new Application();
app.use(router.routes());
app.use(router.allowedMethods());

async function userlist(ctx) {
    ctx.response.body = await render.userList(Object.keys(posts));
}

async function list(ctx) {
    const user = ctx.params.user;
    console.log('user=', user)
    if(!posts[user])
        posts[user]=[];
    console.log('user=', user)
    console.log('posts[user]=', posts[user])
    ctx.response.body = await render.list(user,posts[user]);
}

async function add(ctx) {
    const user = ctx.params.user;
    console.log('user:',user ,',New Add')
    ctx.response.body = await render.newPost(user);
}

async function show(ctx) {
    const user = ctx.params.user;
    const id = ctx.params.id;
    const userPosts = posts[user];
    const post = userPosts ? userPosts[id] : null;
    if (!post) 
        ctx.throw(404, 'invalid post id');
    console.log('user:',user ,',Show')
    ctx.response.body = await render.show(user,post);
}

async function create(ctx) {
    const user = ctx.params.user; //// 從 URL 參數中取得 user, Deno 和 Oak 框架中 request非有效變量
    const body = ctx.request.body;
    if (body.type() === "form") {
        const pairs = await body.form() // body.value
        const post = {}
        for (const [key, value] of pairs) {
           post[key] = value
        }
        console.log('post=', post)
        if(!posts[user])
            posts[user]=[];
        const id = posts[user].push(post) - 1;
        post.Date = new Date();
        post.id = id;
        ctx.response.redirect(`/${user}/`);
  }
}

console.log('Server run at http://127.0.0.1:8000')
await app.listen({ port: 8000 }); 
