import Vue from 'vue';
import StoryV from '@/components/story/story.vue';
import LandingV from '@/components/editor/landing.vue';
import EditorV from '@/components/editor/editor.vue';
import StoryPreviewV from '@/components/editor/preview.vue';
import Router, { Route } from 'vue-router';

Vue.use(Router);

const routes = [
    {
        path: '/',
        component: StoryV,
        meta: { title: 'story.window.title' }
    },
    {
        path: '/:lang/editor',
        name: 'home',
        component: LandingV,
        meta: { title: 'editor.window.title' }
    },
    {
        path: '/:lang/editor-metadata',
        name: 'metadata',
        component: EditorV,
        props: true,
        meta: { title: 'editor.window.title' }
    },
    {
        path: '/:lang/editor/:uid',
        name: 'editor',
        component: EditorV,
        meta: { title: 'editor.window.title' }
    },
    {
        path: '/:lang/editor-preview',
        component: StoryPreviewV,
        name: 'preview',
        props: true,
        meta: { title: 'story.window.title' }
    },
    {
        path: '/:lang/editor-preview/:uid',
        component: StoryPreviewV,
        meta: { title: 'story.window.title' }
    },
    {
        path: '/:uid',
        component: StoryV,
        meta: { title: 'story.window.title' }
    },
    {
        path: '/:lang/:uid',
        component: StoryV,
        meta: { title: 'story.window.title' }
    }
];

export default new Router({
    routes: routes,
    // mode: 'history', // TODO: uncomment to change to history mode for nicer URLs (eliminating middle hash) see #100
    scrollBehavior: function (to: Route) {
        if (to.hash) {
            return {
                selector: decodeURIComponent(to.hash),
                behavior: 'smooth'
            };
        }
    }
});
