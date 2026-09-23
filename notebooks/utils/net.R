######## Functions net


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Attribs_force_atlas_2
#
# Chart line de doble escala del total tweets vs alcance de los mismos
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


set_attrib_force_atlas_2 <- function(g, comm_df, colores_nodos){
  
  # 1. Color
  V(g)$color_node <- colores_nodos

  # 2. Comunidad
  # (los beneficiarios que no son co-retweeters quedan con NA)
  V(g)$community <- comm_df$community[
    match(V(g)$name, comm_df$node)
  ]

  # 3. Grados ponderados (usar SIEMPRE el grafo, no el dataframe)
  V(g)$in_degree_w <- strength(
     g, mode = "in", weights = E(g)$weight
  )

  V(g)$degree_w <- strength(
    g, mode = "all", weights = E(g)$weight
  )

  # 4. Tamaños y etiquetas
  V(g)$size <- scales::rescale(
    V(g)$degree_w, to = c(2, 20)
  )
  umbral_texto <- quantile(V(g)$in_degree_w, 0.70, na.rm = TRUE)
    V(g)$label <- ifelse(
      V(g)$in_degree_w > umbral_texto, # 30% con más in_degree_w
        V(g)$name,
        ""
  )

  V(g)$label_size <- scales::rescale(
    V(g)$in_degree_w, to = c(2, 10)
  )
  # -------------------------------
  # COLORES DE ARISTAS (para ggraph)
  # -------------------------------
  orig <- ends(g, es = E(g), names = TRUE)[,1]
   E(g)$color_edge <- colores_nodos[orig]   # <--- AQUÍ SE ASIGNAN LOS COLORES DE LAS FLECHAS

  return (g)
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# draw_force_atlas_2
#
# Chart line de doble escala del total tweets vs alcance de los mismos
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
draw_force_atlas_2 <- function(g, title, caption) {

   # -------------------------------
   # GRAFO LIMPIO PARA FORCEATLAS2
   # -------------------------------
   layout_g <- g
   layout_g <- delete_edge_attr(layout_g, "color_edge")   # quitar estética
   E(layout_g)$weight <- as.numeric(E(layout_g)$weight)
   E(layout_g)$weight[is.na(E(layout_g)$weight)] <- 1
   
   layout_fa2 <- ForceAtlas2::layout.forceatlas2(
     layout_g,
     iterations = 300,
     gravity    = 2,
     linlog     = TRUE,
     plotstep   = 0
   )
   
   # -------------------------------
   # VISUALIZACIÓN FINAL
   # -------------------------------

   p <- ggraph(g, layout = layout_fa2) +
       geom_edge_link(aes(color = color_edge), alpha = 0.15) +   # <--- AQUÍ SE USAN LOS COLORES
       geom_node_point(aes(color = color_node, size = size)) +
       geom_node_text(aes(label = label, size = label_size), repel = TRUE, max.overlaps = Inf) +
       scale_edge_color_identity() + 
       scale_color_identity() + 
       scale_size_identity() +
       labs(
         title = title,
         caption = caption
       ) +
       theme_graph() +
       theme(
         text = element_text(family = "Arial"),
         legend.position = "none",
         plot.title = element_text(size = 16, color = COLOR_TEXTO),
         plot.caption = element_text(hjust = 1, size = 10, color = COLOR_TEXTO)
       )
  return (p)
}

