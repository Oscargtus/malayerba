# Revisa que .pages.yml (Pages CMS) y los artículos de _posts/ encajen entre sí.
# Uso (desde la carpeta malayerba-jekyll):  ruby tools/verificar-cms.rb
# Lo ejecuta también ./tools/compilar.sh.
#
# Comprueba:
#  - que .pages.yml solo usa opciones que existen en Pages CMS (las de su lib/config-schema.ts)
#  - que las secciones y autores del desplegable coinciden con _data/categorias.yml y _data/autores.yml
#  - que cada artículo cumple las reglas del formulario (obligatorios, valores, rutas de fotos que existen)
require "yaml"
require "date"
Encoding.default_external = Encoding::UTF_8

Dir.chdir(File.expand_path("..", __dir__))
errores = []
avisos = []

cfg = YAML.safe_load(File.read(".pages.yml"))

# ---------- 1. opciones permitidas (Pages CMS, lib/config-schema.ts) ----------
PERMITIDAS = {
  "raiz"      => %w[media content components settings actions],
  "media"     => %w[name label input output path extensions categories rename commit actions],
  "settings"  => %w[config cache hide content commit],
  "contenido" => %w[name label description type path operations filename exclude view fields format
                    delimiters subfolders list commit actions items icon],
  "operations"=> %w[create rename delete],
  "view"      => %w[layout node fields primary sort search default],
  "campo"     => %w[name label description type component default list hidden readonly required pattern
                    options fields blocks blockKey],
}
TIPOS = %w[block boolean code date file image number object reference rich-text select string text uuid]

def revisar_claves(hash, grupo, donde, errores)
  (hash.keys - PERMITIDAS[grupo]).each { |k| errores << "#{donde}: opción desconocida '#{k}'" }
end

revisar_claves(cfg, "raiz", ".pages.yml", errores)
medias = Array(cfg["media"])
medias.each do |m|
  revisar_claves(m, "media", "media '#{m["name"]}'", errores)
  errores << "media '#{m["name"]}': input no puede empezar ni acabar en /" if m["input"].to_s =~ %r{\A/|/\z}
  errores << "media '#{m["name"]}': falta name" if medias.size > 1 && !m["name"]
end
revisar_claves(cfg["settings"] || {}, "settings", "settings", errores)

articulos = cfg["content"].find { |c| c["path"] == "_posts" }
abort "No encuentro la colección de _posts en .pages.yml" unless articulos
revisar_claves(articulos, "contenido", "colección", errores)
revisar_claves(articulos["operations"] || {}, "operations", "operations", errores)
revisar_claves(articulos["view"] || {}, "view", "view", errores)
campos = articulos["fields"].map { |f| [f["name"], f] }.to_h
articulos["fields"].each do |f|
  revisar_claves(f, "campo", "campo '#{f["name"]}'", errores)
  errores << "campo '#{f["name"]}': tipo desconocido '#{f["type"]}'" unless TIPOS.include?(f["type"])
end

# ---------- 2. desplegables = _data ----------
valores = ->(campo) { campos[campo]["options"]["values"].map { |v| v["value"].to_s } }
{ "categoria" => "_data/categorias.yml", "autor" => "_data/autores.yml" }.each do |campo, archivo|
  ids = YAML.safe_load(File.read(archivo)).map { |x| x["id"].to_s }
  faltan = ids - valores.(campo)
  sobran = valores.(campo) - ids
  errores << "#{archivo} tiene #{faltan.join(", ")} pero el desplegable '#{campo}' de .pages.yml no" if faltan.any?
  errores << "el desplegable '#{campo}' de .pages.yml tiene #{sobran.join(", ")} pero #{archivo} no" if sobran.any?
end

# ---------- 3. artículos ----------
carpeta_media = ->(campo) do
  nombre = campos[campo].dig("options", "media")
  m = nombre ? medias.find { |x| x["name"] == nombre } : medias.first
  [m["input"], Array(m["extensions"])]
end

Dir["_posts/*.md"].sort.each do |ruta|
  fm = YAML.safe_load(File.read(ruta)[/\A---\n(.*?)\n---/m, 1], permitted_classes: [Date, Time])
  n = File.basename(ruta)
  campos.each do |nombre, f|
    next if nombre == "body"
    v = fm[nombre]
    vacio = v.nil? || v.to_s.strip.empty?
    if f["required"] && vacio
      errores << "#{n}: falta '#{nombre}' (obligatorio)"
      next
    end
    next if vacio
    case f["type"]
    when "select"
      errores << "#{n}: '#{nombre}' debe ser texto entre comillas (\"#{v}\")" unless v.is_a?(String)
      errores << "#{n}: '#{nombre}' = #{v} no está en el desplegable" unless valores.(nombre).include?(v.to_s)
    when "image"
      carpeta, exts = carpeta_media.(nombre)
      errores << "#{n}: '#{nombre}' debe estar en #{carpeta}/ (#{v})" unless v.start_with?("#{carpeta}/")
      errores << "#{n}: '#{nombre}' debe ser #{exts.join("/")} (#{v})" unless exts.include?(File.extname(v).delete(".").downcase)
      errores << "#{n}: no existe el archivo #{v}" unless File.exist?(v)
    when "boolean"
      errores << "#{n}: '#{nombre}' debe ser true o false" unless [true, false].include?(v)
    when "string", "text"
      if f["list"]
        errores << "#{n}: '#{nombre}' debe ser una lista" unless v.is_a?(Array) && v.all? { |x| x.is_a?(String) }
      else
        errores << "#{n}: '#{nombre}' debe ser texto" unless v.is_a?(String)
      end
    end
  end
  extra = fm.keys - campos.keys
  avisos << "#{n}: se conservan sin formulario: #{extra.join(", ")}" if extra.any?
end

avisos.each { |a| puts "  · #{a}" }
if errores.empty?
  puts "✓ Pages CMS: .pages.yml y los #{Dir["_posts/*.md"].size} artículos encajan."
else
  puts "✗ Pages CMS: hay que corregir:"
  errores.each { |e| puts "  - #{e}" }
  exit 1
end
