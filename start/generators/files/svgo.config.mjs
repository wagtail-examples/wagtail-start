export default {
    plugins: [
      {
        name: 'preset-default',
        params: {
          overrides: {
            // disable a default plugin
            removeViewBox: false,
            removeTitle: false,

            // customize the params of a default plugin
            inlineStyles: {
              onlyMatchedOnce: false,
            },
          },
        },
      },
    ],
  };
